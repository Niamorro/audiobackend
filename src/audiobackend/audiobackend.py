# audiobackend.py
import av
import sounddevice as sd
import numpy as np
from typing import Callable
import time
import threading
import os

class AudioBackend:
    def __init__(self):
        # Main parameters
        self._container = None
        self._stream = None
        self._playing = False
        self._position = 0
        self._duration = 0
        self._volume = 1.0
        self._current_file = None
        self._resampler = None
        
        # Buffer parameters
        self._buffer = None
        self._buffer_size = 65536
        self._min_buffer_size = 32768
        self._max_buffer_frames = 262144
        self._prebuffer_size = 16384
        self._buffer_threshold = 0.6
        
        # Audio parameters
        self._sample_rate = 48000
        self._preferred_sample_rate = 48000
        self._max_supported_rate = 384000  # Maximum supported frequency
        self._original_sample_rate = None  # To store the original frequency
        self._channels = 2
        
        # Callbacks
        self._position_callback = None
        self._playback_state_callback = None
        self._end_of_track_callback = None
        
        # Thread control
        self._buffer_thread = None
        self._buffer_lock = threading.Lock()
        self._buffer_event = threading.Event()
        self._loading_lock = threading.Lock()
        
        # State
        self._seek_requested = False
        self._seek_position = 0
        self._position_update_interval = 50
        self._last_position_update = 0
        self._switching_tracks = False
        self._underflow_count = 0
        self._last_underflow = 0
        
        # Better seek
        self._skip_packets_after_seek = 2
        self._packets_skipped = 0
        self._seek_tolerance = 0.5
        self._seek_error_count = 0
        self._max_seek_errors = 3

        # Logging
        self._last_buffer_log = 0
        self._buffer_log_interval = 1000
        self._debug_buffer = True

    def load_file(self, file_path: str) -> bool:
        with self._loading_lock:
            if self._switching_tracks:
                return False
                
            try:
                self._switching_tracks = True
                
                if self._playing:
                    self.pause()
                
                self._cleanup(full=False)
                
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    return False

                self._current_file = file_path
                print(f"Loading file: {file_path}")
                
                # Reset the track end flag
                if hasattr(self, '_end_reported'):
                    delattr(self, '_end_reported')
                
                try:
                    self._container = av.open(file_path, options={
                        'analyzeduration': '5000000',
                        'probesize': '5000000',
                        'thread_count': '4'
                    })
                    
                    stream = self._container.streams.audio[0]
                    self._duration = int(stream.duration * stream.time_base * 1000)
                    
                    if self._duration <= 0:
                        raise ValueError("Invalid duration detected")

                    # Get and save the original frequency
                    original_sample_rate = stream.rate
                    self._original_sample_rate = original_sample_rate
                    print(f"Original sample rate: {original_sample_rate} Hz")

                    # Determine the optimal sampling rate
                    target_sample_rate = self._preferred_sample_rate

                    # For very high frequencies (DSD)
                    if original_sample_rate > self._max_supported_rate:
                        # Find the highest supported frequency
                        target_sample_rate = self._max_supported_rate
                        print(f"Original rate {original_sample_rate} Hz is too high, downsampling to {target_sample_rate} Hz")
                    elif original_sample_rate > self._preferred_sample_rate:
                        target_sample_rate = original_sample_rate
                        print(f"Using original sample rate: {target_sample_rate} Hz")
                    else:
                        print(f"Using preferred sample rate: {target_sample_rate} Hz")

                    # Create a high quality resampler
                    self._resampler = av.AudioResampler(
                        format=av.AudioFormat('flt'),
                        layout='stereo',
                        rate=target_sample_rate
                    )

                    print(f"Resampler configured: {original_sample_rate} Hz -> {target_sample_rate} Hz")

                    # Recreate the stream
                    if self._stream is not None:
                        if self._stream.active:
                            self._stream.stop()
                        self._stream.close()
                        self._stream = None

                    try:
                        self._stream = sd.OutputStream(
                            samplerate=target_sample_rate,
                            channels=self._channels,
                            dtype=np.float32,
                            callback=self._audio_callback,
                            finished_callback=self._stream_finished_callback
                        )
                    except Exception as e:
                        print(f"Failed to create stream with {target_sample_rate} Hz, falling back to {self._preferred_sample_rate} Hz")
                        target_sample_rate = self._preferred_sample_rate
                        self._resampler = av.AudioResampler(
                            format=av.AudioFormat('flt'),
                            layout='stereo',
                            rate=target_sample_rate
                        )
                        self._stream = sd.OutputStream(
                            samplerate=target_sample_rate,
                            channels=self._channels,
                            dtype=np.float32,
                            callback=self._audio_callback,
                            finished_callback=self._stream_finished_callback
                        )

                    self._sample_rate = target_sample_rate
                    print("Final playback configuration:")
                    print(f"- Original rate: {self._original_sample_rate} Hz")
                    print(f"- Playback rate: {self._sample_rate} Hz")
                    print(f"- Channels: {self._channels}")

                    # Buffer initialization
                    self._buffer = np.zeros((0, self._channels), dtype=np.float32)
                    self._position = 0
                    self._seek_requested = False
                    self._packets_skipped = 0
                    self._seek_error_count = 0
                    self._underflow_count = 0

                    # Restart the buffer filling thread
                    if self._buffer_thread is None or not self._buffer_thread.is_alive():
                        self._buffer_thread = threading.Thread(target=self._buffer_filler, daemon=True)
                        self._buffer_thread.start()

                    # Waiting for the initial buffer filling
                    wait_start = time.time()
                    while len(self._buffer) < self._prebuffer_size * 0.5 and time.time() - wait_start < 1.0:
                        time.sleep(0.01)

                    # Start the stream
                    self._stream.start()
                    return True

                except Exception as e:
                    print(f"Error opening audio file: {e}")
                    self._cleanup(full=True)
                    return False

            except Exception as e:
                print(f"Error loading file: {e}")
                self._cleanup(full=True)
                return False
            finally:
                self._switching_tracks = False

    def _audio_callback(self, outdata, frames, time_info, status):
        current_time = time.time() * 1000

        if status and status.output_underflow:
            print(f"[WARNING] Buffer underflow detected at position {self._position}ms")
            self._buffer_event.set()

        with self._buffer_lock:
            if not self._playing or len(self._buffer) == 0:
                outdata.fill(0)
                self._log_buffer_state("audio_callback_empty")
                
                # Checking to see if the track is really over
                if self._position >= self._duration - 100:  # a small margin of 100ms
                    if not hasattr(self, '_end_reported'):
                        self._end_reported = True
                        # Use Timer to avoid calling the callback inside the callback
                        threading.Timer(0.1, self._handle_end_of_track).start()
                return

            frames_needed = frames
            available_frames = len(self._buffer)

            if available_frames >= frames_needed:
                outdata[:] = self._buffer[:frames_needed] * self._volume
                self._buffer = self._buffer[frames_needed:]
                
                frames_duration = int(frames * 1000 / self._sample_rate)
                self._position += frames_duration
                
                if len(self._buffer) < self._buffer_size * 0.5:
                    self._buffer_event.set()
            else:
                outdata[:available_frames] = self._buffer * self._volume
                outdata[available_frames:].fill(0)
                self._buffer = np.zeros((0, self._channels), dtype=np.float32)
                self._buffer_event.set()

            if current_time - self._last_position_update >= self._position_update_interval:
                if self._position_callback:
                    self._position_callback(self._position)
                self._last_position_update = current_time
                self._log_buffer_state("audio_callback_update")

    def _buffer_filler(self):
        print("Buffer filler thread started")
        
        while True:
            if not self._playing or not self._container:
                time.sleep(0.01)
                continue

            try:
                with self._buffer_lock:
                    current_buffer_size = len(self._buffer)
                    if current_buffer_size >= self._max_buffer_frames:
                        self._buffer_event.wait(0.01)
                        continue
                    
                    if current_buffer_size > self._buffer_size * self._buffer_threshold:
                        self._buffer_event.wait(0.01)
                        continue

                stream = self._container.streams.audio[0]
                
                for packet in self._container.demux(stream):
                    if not self._playing or self._seek_requested:
                        break

                    try:
                        frames = packet.decode()
                        if not frames:
                            continue

                        for frame in frames:
                            resampled_frames = self._resampler.resample(frame)
                            for resampled in resampled_frames:
                                audio_array = resampled.to_ndarray().reshape(-1, self._channels)
                                
                                with self._buffer_lock:
                                    if len(self._buffer) + len(audio_array) > self._max_buffer_frames:
                                        break
                                    
                                    self._buffer = np.vstack([self._buffer, audio_array])
                                    
                                    if len(self._buffer) >= self._buffer_size:
                                        break

                        if len(self._buffer) >= self._buffer_size:
                            break

                    except Exception as e:
                        print(f"[ERROR] Frame processing error: {e}")
                        continue

            except av.error.EOFError:
                print("[INFO] Buffer filler: EOF reached")
                self._handle_end_of_track()
            except Exception as e:
                print(f"[ERROR] Buffer filler error: {e}")
                time.sleep(0.1)

    def _check_playback_state(self):
        self._monitor_buffer_health()
        if self._position > 0 and len(self._buffer) > 0 and not self._playing:
            print("[WARNING] Inconsistent playback state detected, attempting to recover")
            self._playing = True
            if self._playback_state_callback:
                self._playback_state_callback(True)
        
    def _monitor_buffer_health(self):
        with self._buffer_lock:
            buffer_size = len(self._buffer)
            if buffer_size > self._max_buffer_frames:
                self._reset_buffer_if_needed()
            elif buffer_size < self._min_buffer_size and self._playing:
                print("[WARNING] Buffer health check: Buffer too small")
                self._buffer_event.set()
            
        if self._underflow_count > 5:
            print("[WARNING] Too many underflows, attempting recovery")
            self._underflow_count = 0
            self._buffer_size = min(self._buffer_size * 1.5, self._max_buffer_frames)
            self._buffer_event.set()

    def _reset_buffer_if_needed(self):
        with self._buffer_lock:
            if len(self._buffer) > self._max_buffer_frames:
                print("[WARNING] Buffer overflow detected, resetting buffer")
                self._buffer = self._buffer[:self._max_buffer_frames]
                return True
        return False

    def _log_buffer_state(self, context: str):
        if not self._debug_buffer:
            return
            
        current_time = time.time() * 1000
        if current_time - self._last_buffer_log < self._buffer_log_interval:
            return
            
        self._last_buffer_log = current_time
        buffer_length = len(self._buffer) if self._buffer is not None else 0
        buffer_duration = buffer_length / self._sample_rate if buffer_length > 0 else 0
        
        print(f"[{context}] Buffer state:")
        print(f"  - Size: {buffer_length} frames ({buffer_length * 4 / 1024:.2f} KB)")
        print(f"  - Duration: {buffer_duration:.3f} sec")
        print(f"  - Capacity: {(buffer_length / self._buffer_size * 100):.1f}%")
        print(f"  - Position: {self._position} ms")
        print(f"  - Playing: {self._playing}")
        print(f"  - Underflow count: {self._underflow_count}")

    def seek(self, position_ms: int):
        if not self._container or not self._stream:
            print("[ERROR] Cannot seek: no audio file loaded")
            return

        position_ms = max(0, min(position_ms, self._duration))
        print(f"[DEBUG] Seeking to position: {position_ms}ms")
        self._log_buffer_state("seek_start")
        
        try:
            with self._loading_lock:
                if self._switching_tracks:
                    print("[WARNING] Cannot seek while switching tracks")
                    return

                was_playing = self._playing
                if self._playing:
                    self.pause()

                self._position = position_ms
                if self._position_callback:
                    self._position_callback(position_ms)

                def seek_thread():
                    try:
                        with self._buffer_lock:
                            self._seek_requested = True
                            self._seek_position = position_ms
                            self._buffer = np.zeros((0, self._channels), dtype=np.float32)
                            self._packets_skipped = 0
                            print("[DEBUG] Buffer cleared for seeking")

                        stream = self._container.streams.audio[0]
                        seek_point = int((position_ms / 1000.0) / stream.time_base)
                        
                        try:
                            self._container.seek(seek_point, stream=stream, any_frame=True)
                            print("[DEBUG] Primary seek successful")
                        except:
                            try:
                                self._container.seek(seek_point, stream=stream, backward=True)
                                print("[DEBUG] Fallback seek successful")
                            except Exception as e:
                                print(f"[ERROR] Seek failed: {e}")
                                self._seek_error_count += 1
                                if self._seek_error_count >= self._max_seek_errors:
                                    return self._handle_seek_error()
                                return

                        self._seek_error_count = 0
                        
                        with self._buffer_lock:
                            self._seek_requested = False
                            print("[DEBUG] Seek completed")
                        
                        self._buffer_event.set()
                        self._log_buffer_state("seek_complete")
                        
                        if was_playing:
                            self.play()

                    except Exception as e:
                        print(f"[ERROR] Error in seek thread: {e}")
                        self._handle_seek_error()

                seek_thread = threading.Thread(target=seek_thread, daemon=True)
                seek_thread.start()
                seek_thread.join(timeout=0.1)

        except Exception as e:
            print(f"[ERROR] Critical seek error: {e}")
            self._handle_seek_error()

    def _handle_seek_error(self):
        print("Handling seek error, attempting to recover...")
        with self._buffer_lock:
            self._seek_requested = False
            self._buffer = np.zeros((0, self._channels), dtype=np.float32)
        
        if self._seek_error_count >= self._max_seek_errors:
            print("Too many seek errors, reloading file...")
            self._seek_error_count = 0
            if self._current_file:
                self.load_file(self._current_file)

    def play(self):
        if not self._playing and self._stream:
            print("Starting playback")
            self._playing = True
            if not self._stream.active:
                self._stream.start()
            if self._playback_state_callback:
                self._playback_state_callback(True)

    def pause(self):
        if self._playing:
            print("Pausing playback")
            self._playing = False
            if self._playback_state_callback:
                self._playback_state_callback(False)

    def stop(self):
        print("Stopping playback")
        self._playing = False
        self._cleanup(full=True)
        if self._playback_state_callback:
            self._playback_state_callback(False)

    def set_volume(self, volume: float):
        self._volume = max(0.0, min(1.0, volume))

    def _cleanup(self, full=True):
        print("Cleaning up resources")
        self._playing = False
        
        with self._buffer_lock:
            self._buffer = np.zeros((0, self._channels), dtype=np.float32)
        
        if full:
            if self._stream is not None:
                try:
                    if self._stream.active:
                        self._stream.stop()
                    self._stream.close()
                except Exception as e:
                    print(f"Error closing stream: {e}")
                finally:
                    self._stream = None

            if self._container is not None:
                try:
                    self._container.close()
                except Exception as e:
                    print(f"Error closing container: {e}")
                finally:
                    self._container = None

            self._resampler = None
            self._current_file = None
        
        self._position = 0
        self._seek_requested = False
        self._last_position_update = 0
        self._seek_error_count = 0

    def reset_state(self):
        try:
            print("Resetting player state")
            if self._stream and self._stream.active:
                self._stream.stop()
            
            if self._container:
                stream = self._container.streams.audio[0]
                self._container.seek(0, stream=stream, any_frame=True)
                
            with self._buffer_lock:
                self._buffer = np.zeros((0, self._channels), dtype=np.float32)
                self._position = 0
                self._seek_requested = False
                self._packets_skipped = 0
                
            # Recreate the stream
            if self._stream:
                self._stream.close()
                self._stream = sd.OutputStream(
                    samplerate=self._sample_rate,
                    channels=self._channels,
                    dtype=np.float32,
                    callback=self._audio_callback,
                    finished_callback=self._stream_finished_callback
                )
            
            self._buffer_event.set()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to reset state: {e}")
            return False
        
    def cleanup_stream(self):
        if self._stream:
            try:
                if self._stream.active:
                    self._stream.stop()
                self._stream.close()
            except Exception as e:
                print(f"Error cleaning up stream: {e}")
            finally:
                self._stream = None

        try:
            self._stream = sd.OutputStream(
                samplerate=self._sample_rate,
                channels=self._channels,
                dtype=np.float32,
                callback=self._audio_callback,
                finished_callback=self._stream_finished_callback
            )
        except Exception as e:
            print(f"Error creating new stream: {e}")

    def _stream_finished_callback(self):
        print("Stream finished callback called")
        self._handle_end_of_track()

    def _handle_end_of_track(self):
        print("Handling end of track")
        if hasattr(self, '_end_being_handled'):
            return
        
        self._end_being_handled = True
        try:
            if not self._switching_tracks:
                self._playing = False
                self._position = self._duration
                
                with self._buffer_lock:
                    self._buffer = np.zeros((0, self._channels), dtype=np.float32)
                
                if self._stream and self._stream.active:
                    self._stream.stop()
                
                try:
                    if self._position_callback:
                        self._position_callback(self._position)
                    if self._playback_state_callback:
                        self._playback_state_callback(False)
                    if self._end_of_track_callback:
                        self._end_of_track_callback()
                except Exception as e:
                    print(f"[ERROR] Error in end of track handling: {e}")
        finally:
            delattr(self, '_end_being_handled')

    def set_position_callback(self, callback: Callable[[int], None]):
        self._position_callback = callback

    def set_playback_state_callback(self, callback: Callable[[bool], None]):
        self._playback_state_callback = callback

    def set_end_of_track_callback(self, callback: Callable[[], None]):
        self._end_of_track_callback = callback

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def position(self) -> int:
        return self._position

    @property
    def is_playing(self) -> bool:
        return self._playing

    def __del__(self):
        try:
            if hasattr(self, '_playing'):
                self.stop()
        except Exception as e:
            print(f"Error in destructor: {e}")
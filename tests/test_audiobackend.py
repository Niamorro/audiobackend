import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from audiobackend import AudioBackend

@pytest.fixture
def mock_sounddevice():
    with patch('sounddevice.OutputStream') as mock_output_stream:
        # Create a mock stream instance
        mock_stream = MagicMock()
        mock_output_stream.return_value = mock_stream
        yield mock_output_stream

@pytest.fixture
def mock_av():
    with patch('av.open') as mock_av_open:
        # Create mock container and stream
        mock_container = MagicMock()
        mock_stream = MagicMock()
        mock_stream.duration = 1000000  # 1000 seconds in stream timebase
        mock_stream.time_base = 0.001   # timebase for converting to milliseconds
        mock_stream.rate = 48000        # sample rate
        
        # Set up container mock
        mock_container.streams.audio = [mock_stream]
        mock_av_open.return_value = mock_container
        
        yield mock_av_open

@pytest.fixture
def audio_backend(mock_sounddevice, mock_av):
    backend = AudioBackend()
    yield backend
    backend.stop()

def test_init(audio_backend):
    """Test initialization of AudioBackend"""
    assert audio_backend._playing is False
    assert audio_backend._position == 0
    assert audio_backend._volume == 1.0
    assert audio_backend._sample_rate == 48000
    assert audio_backend._channels == 2

def test_load_file_success(audio_backend, mock_av, tmp_path):
    """Test successful file loading"""
    # Create a temporary file
    test_file = tmp_path / "test_audio.mp3"
    test_file.write_bytes(b"dummy content")
    
    with patch('os.path.exists', return_value=True):
        result = audio_backend.load_file(str(test_file))
        assert result is True
        assert audio_backend._duration == 1000000
        mock_av.assert_called_once()

def test_load_file_nonexistent(audio_backend):
    """Test loading non-existent file"""
    result = audio_backend.load_file("nonexistent.mp3")
    assert result is False

def test_play_pause(audio_backend):
    """Test play and pause functionality"""
    # Mock callbacks
    playback_callback = Mock()
    audio_backend.set_playback_state_callback(playback_callback)
    
    # Test play
    audio_backend._stream = MagicMock()  # Mock stream for testing
    audio_backend.play()
    assert audio_backend.is_playing is True
    playback_callback.assert_called_with(True)
    
    # Test pause
    audio_backend.pause()
    assert audio_backend.is_playing is False
    playback_callback.assert_called_with(False)

def test_volume_control(audio_backend):
    """Test volume control"""
    # Test normal volume
    audio_backend.set_volume(0.5)
    assert audio_backend._volume == 0.5
    
    # Test volume limits
    audio_backend.set_volume(1.5)  # Should clamp to 1.0
    assert audio_backend._volume == 1.0
    
    audio_backend.set_volume(-0.5)  # Should clamp to 0.0
    assert audio_backend._volume == 0.0

def test_seek(audio_backend):
    """Test seek functionality"""
    # Setup
    audio_backend._container = MagicMock()
    audio_backend._stream = MagicMock()
    audio_backend._duration = 5000  # 5 seconds
    
    # Mock position callback
    position_callback = Mock()
    audio_backend.set_position_callback(position_callback)
    
    # Test normal seek
    audio_backend.seek(2000)  # Seek to 2 seconds
    assert audio_backend._position == 2000
    position_callback.assert_called_with(2000)
    
    # Test seek beyond duration
    audio_backend.seek(6000)  # Should clamp to duration
    assert audio_backend._position == 5000
    position_callback.assert_called_with(5000)
    
    # Test negative seek
    audio_backend.seek(-1000)  # Should clamp to 0
    assert audio_backend._position == 0
    position_callback.assert_called_with(0)

def test_end_of_track_callback(audio_backend):
    """Test end of track callback"""
    end_callback = Mock()
    audio_backend.set_end_of_track_callback(end_callback)
    
    # Simulate end of track
    audio_backend._handle_end_of_track()
    
    # Verify callback was called
    end_callback.assert_called_once()
    assert audio_backend.is_playing is False

@pytest.mark.parametrize("buffer_size", [
    32768,  # Minimum buffer size
    65536,  # Default buffer size
    262144  # Maximum buffer size
])
def test_buffer_management(audio_backend, buffer_size):
    """Test buffer management with different sizes"""
    audio_backend._buffer_size = buffer_size
    audio_backend._buffer = np.zeros((buffer_size, 2), dtype=np.float32)
    
    # Test buffer reset
    audio_backend._reset_buffer_if_needed()
    assert len(audio_backend._buffer) <= audio_backend._max_buffer_frames

def test_cleanup(audio_backend):
    """Test cleanup functionality"""
    # Setup mocks
    audio_backend._stream = MagicMock()
    audio_backend._container = MagicMock()
    
    # Perform cleanup
    audio_backend._cleanup(full=True)
    
    # Verify cleanup
    assert audio_backend._playing is False
    assert audio_backend._position == 0
    assert audio_backend._stream is None
    assert audio_backend._container is None
    assert len(audio_backend._buffer) == 0

def test_audio_callback(audio_backend):
    """Test audio callback functionality"""
    # Setup test buffer
    test_frames = 1024
    audio_backend._buffer = np.ones((2048, 2), dtype=np.float32)
    audio_backend._playing = True
    audio_backend._volume = 0.5
    
    # Create output buffer
    outdata = np.zeros((test_frames, 2), dtype=np.float32)
    
    # Call callback
    audio_backend._audio_callback(outdata, test_frames, None, None)
    
    # Verify output
    assert np.all(outdata == 0.5)  # Should be filled with 0.5 due to volume
    assert len(audio_backend._buffer) == 1024  # Should have consumed test_frames

def test_reset_state(audio_backend):
    """Test state reset functionality"""
    # Setup initial state
    audio_backend._stream = MagicMock()
    audio_backend._container = MagicMock()
    audio_backend._position = 1000
    audio_backend._buffer = np.ones((1000, 2), dtype=np.float32)
    
    # Reset state
    result = audio_backend.reset_state()
    
    # Verify reset
    assert result is True
    assert audio_backend._position == 0
    assert len(audio_backend._buffer) == 0
    assert audio_backend._seek_requested is False
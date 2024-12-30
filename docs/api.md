# API Reference

## AudioBackend Class

!!! tip "Main Class"
    The AudioBackend class is the primary interface for audio playback functionality.

### Constructor

```python
player = AudioBackend()
```

Creates a new instance of the AudioBackend player with default settings.

### Methods

#### File Operations

##### `load_file()`

```python
def load_file(file_path: str) -> bool
```

Loads an audio file for playback.

**Parameters:**

- `file_path` (str): Path to the audio file

**Returns:**

- `bool`: True if file loaded successfully, False otherwise

**Example:**
```python
success = player.load_file("music.mp3")
if not success:
    print("Failed to load file")
```

#### Playback Control

##### `play()`

```python
def play() -> None
```

Starts or resumes playback.

---

##### `pause()`

```python
def pause() -> None
```

Pauses playback.

---

##### `stop()`

```python
def stop() -> None
```

Stops playback and releases resources.

---

##### `seek()`

```python
def seek(position_ms: int) -> None
```

Seeks to specified position.

**Parameters:**

- `position_ms` (int): Position to seek to in milliseconds

---

##### `set_volume()`

```python
def set_volume(volume: float) -> None
```

Sets playback volume.

**Parameters:**

- `volume` (float): Volume level between 0.0 and 1.0

#### Callback Management

##### `set_position_callback()`

```python
def set_position_callback(callback: Callable[[int], None]) -> None
```

Sets callback for position updates.

**Parameters:**

- `callback` (Callable[[int], None]): Function that receives position in milliseconds

---

##### `set_playback_state_callback()`

```python
def set_playback_state_callback(callback: Callable[[bool], None]) -> None
```

Sets callback for playback state changes.

**Parameters:**

- `callback` (Callable[[bool], None]): Function that receives boolean playing state

---

##### `set_end_of_track_callback()`

```python
def set_end_of_track_callback(callback: Callable[[], None]) -> None
```

Sets callback for track end notification.

**Parameters:**

- `callback` (Callable[[], None]): Function called when track ends

### Properties

#### `duration`

```python
@property
def duration(self) -> int
```

Gets the duration of the current track in milliseconds.

---

#### `position`

```python
@property
def position(self) -> int
```

Gets the current playback position in milliseconds.

---

#### `is_playing`

```python
@property
def is_playing(self) -> bool
```

Gets the current playback state.

### Technical Details

#### Buffer Management

| Parameter | Size (frames) | Description |
|-----------|--------------|-------------|
| Default buffer | 65536 | Standard buffer size |
| Minimum buffer | 32768 | Minimum allowed size |
| Maximum buffer | 262144 | Maximum allowed size |
| Prebuffer | 16384 | Initial buffer before playback |

#### Audio Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Default sample rate | 48000 Hz | Standard playback rate |
| Maximum rate | 384000 Hz | Maximum supported rate |
| Channels | 2 | Stereo output |

#### Error Recovery

The system includes:

- Automatic buffer underrun recovery
- Sample rate adaptation
- Stream recreation on errors
- Seek error handling
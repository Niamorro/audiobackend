# Usage Guide

## Basic Usage

### Quick Start

Create a player and start playing audio:

```python
from audiobackend import AudioBackend

# Initialize player
player = AudioBackend()

# Load and play audio
player.load_file("music.mp3")
player.play()
```

### Playback Controls

Control your audio playback with these methods:

```python
# Basic controls
player.pause()    # Pause playback
player.play()     # Resume playback
player.stop()     # Stop completely

# Volume control (0.0 to 1.0)
player.set_volume(0.8)

# Seeking (in milliseconds)
player.seek(60000)  # Seek to 1 minute
```

## Advanced Features

### Event Callbacks

AudioBackend provides a comprehensive callback system:

```python
# Track position updates
def on_position(position_ms: int):
    minutes = position_ms // 60000
    seconds = (position_ms % 60000) // 1000
    print(f"Position: {minutes}:{seconds:02d}")

# Playback state changes
def on_playback_state(is_playing: bool):
    state = "playing" if is_playing else "paused"
    print(f"Playback {state}")

# Track completion
def on_track_end():
    print("Track finished")

# Register callbacks
player.set_position_callback(on_position)
player.set_playback_state_callback(on_playback_state)
player.set_end_of_track_callback(on_track_end)
```

### Resource Management

Use context managers or try-finally for proper cleanup:

```python
# Option 1: Manual cleanup
try:
    player = AudioBackend()
    player.load_file("music.mp3")
    player.play()
    # ... your code ...
finally:
    player.stop()
```

## Best Practices

### Performance Optimization

1. **Player Reuse**
    ```python
    # Good - reuse player
    player = AudioBackend()
    for file in files:
        player.load_file(file)
        player.play()
        
    # Bad - creating multiple instances
    for file in files:
        player = AudioBackend()  # Don't do this
        player.load_file(file)
    ```

2. **Buffer Management**
    ```python
    # For low-latency applications
    player.load_file(file)
    player.play()  # Starts playing as soon as initial buffer is ready
    ```

### Error Handling

Always check return values and handle errors:

```python
# Load file with error checking
if not player.load_file("music.mp3"):
    print("Failed to load file")
    # Handle error...

# Handle playback errors
try:
    player.play()
except Exception as e:
    print(f"Playback error: {e}")
    # Handle error...
```

## Examples

### Simple Music Player

```python
from audiobackend import AudioBackend
import time

def create_music_player():
    player = AudioBackend()
    
    def format_time(ms):
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        return f"{minutes}:{seconds:02d}"
    
    def update_position(pos):
        print(f"\rPosition: {format_time(pos)}", end="")
    
    player.set_position_callback(update_position)
    
    return player

# Usage
player = create_music_player()
player.load_file("music.mp3")
player.play()

# Keep program running
try:
    while player.is_playing:
        time.sleep(0.1)
except KeyboardInterrupt:
    player.stop()
```

### Playlist Implementation

```python
class Playlist:
    def __init__(self):
        self.player = AudioBackend()
        self.tracks = []
        self.current_index = 0
        
        def on_track_end():
            self.play_next()
            
        self.player.set_end_of_track_callback(on_track_end)
    
    def add_track(self, file_path):
        self.tracks.append(file_path)
    
    def play_next(self):
        if self.current_index < len(self.tracks) - 1:
            self.current_index += 1
            self.player.load_file(self.tracks[self.current_index])
            self.player.play()
    
    def play(self):
        if self.tracks:
            self.player.load_file(self.tracks[self.current_index])
            self.player.play()
```
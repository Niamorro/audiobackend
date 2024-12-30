# audiobackend

A high-quality audio playback library for Python with DSD support and efficient buffer management.

## Features

- High-quality audio playback with various formats support (MP3, WAV, FLAC, DSD)
- Efficient buffer management for optimal memory usage
- Automatic sample rate detection and resampling
- Thread-safe implementation
- Simple and intuitive API

## Installation

```bash
pip install audiobackend
```

### Requirements

- Python 3.7 or higher
- FFmpeg (required by PyAV)

#### System Dependencies

Ubuntu/Debian:
```bash
sudo apt-get install libav-tools portaudio19-dev
```

macOS:
```bash
brew install ffmpeg portaudio
```

Windows:
- FFmpeg and PortAudio are included in the package dependencies

## Quick Example

```python
from audiobackend import AudioBackend

player = AudioBackend()
player.load_file("music.mp3")
player.play()
```

## Documentation

For detailed information about usage, API reference, and advanced features, visit our [documentation](https://niamorro.github.io/audiobackend/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.
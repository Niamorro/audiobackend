# audiobackend

A high-quality audio playback library for Python with DSD support and efficient buffer management.

<div align="center">

---

[![Tests](https://img.shields.io/github/actions/workflow/status/Niamorro/audiobackend/tests.yml?style=for-the-badge&logo=github&label=Tests)](https://github.com/Niamorro/audiobackend/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/codecov/c/github/Niamorro/audiobackend?style=for-the-badge&logo=codecov&labelColor=2B2D3A)](https://codecov.io/gh/Niamorro/audiobackend)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python&logoColor=white&labelColor=2B2D3A)](https://pypi.org/project/audiobackend/)
[![License](https://img.shields.io/badge/License-GPL%203.0-green.svg?style=for-the-badge&labelColor=2B2D3A)](https://opensource.org/licenses/GPL-3.0)
[![PyPI version](https://img.shields.io/pypi/v/audiobackend.svg?style=for-the-badge&logo=pypi&logoColor=white&labelColor=2B2D3A)](https://pypi.org/project/audiobackend/)
[![Downloads](https://img.shields.io/pypi/dm/audiobackend?style=for-the-badge&logo=python&labelColor=2B2D3A)](https://pypi.org/project/audiobackend/)

---

</div>


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
sudo apt update
sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev
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
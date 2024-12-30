# AudioBackend

AudioBackend is a high-quality audio playback library with DSD support and efficient buffer management. It provides a robust and flexible solution for audio playback in Python applications.

## Key Features

- **High-Quality Audio Playback**: Support for various audio formats including DSD
- **Efficient Buffer Management**: Optimized buffering system for smooth playback
- **Automatic Sample Rate Detection**: Smart handling of different sample rates
- **Thread-Safe Operations**: Reliable concurrent operation handling
- **Comprehensive Error Handling**: Error recovery system
- **Callback System**: Rich event notification system

## Project Overview

AudioBackend is designed to provide a simple yet powerful interface for audio playback in Python applications. Whether you're building a music player, audio processing application, or need high-quality audio playback in your project, AudioBackend offers the features you need.

```python
from audiobackend import AudioBackend

# Create player instance
player = AudioBackend()

# Load and play audio
player.load_file("music.mp3")
player.play()
```

## Quick Navigation

- **[Installation Guide](installation.md)**: Get started with AudioBackend
- **[Usage Guide](usage.md)**: Learn how to use AudioBackend
- **[API Reference](api.md)**: Detailed API documentation
- **[Contributing Guide](contributing.md)**: Help improve AudioBackend

## Support

- Create an issue on [GitHub](https://github.com/Niamorro/audiobackend/issues)
- Check out the [Contributing Guide](contributing.md)

## License

AudioBackend is released under the GPL-3.0 License. See the [LICENSE](https://github.com/Niamorro/audiobackend/blob/main/LICENSE) file for details.
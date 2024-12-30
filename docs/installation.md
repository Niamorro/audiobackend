# Installation

## Prerequisites

Before installing AudioBackend, make sure you have:

- Python 3.7 or higher
- pip package manager

!!! tip "Virtual Environment"
    It's recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

## Installation Methods

### From PyPI

The recommended way to install AudioBackend:

```bash
pip install audiobackend
```

### From Source

For the latest development version:

```bash
git clone https://github.com/Niamorro/audiobackend.git
cd audiobackend
pip install -e .
```

### Development Installation

For contributing or development:

```bash
pip install -e .[dev]
```

## System Dependencies

=== "Ubuntu/Debian"
    ```bash
    sudo apt update
    sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev
    ```

=== "Fedora/Red Hat"
    ```bash
    sudo dnf install portaudio-devel
    ```

=== "Arch Linux"
    ```bash
    sudo pacman -S portaudio
    ```

=== "macOS"
    ```bash
    brew install ffmpeg portaudio
    ```

=== "Windows"
    FFmpeg is included in the PyAV package.
    For PortAudio, it's included in the sounddevice package.

## Troubleshooting

### Common Issues

??? question "ImportError: No module named 'av'"
    This usually means PyAV installation failed. Try:
    ```bash
    pip install --upgrade av
    ```

??? question "PortAudio not found"
    Install the PortAudio development package for your system (see System Dependencies above)

??? question "Version conflicts"
    ```bash
    pip install --upgrade pip
    pip install --upgrade audiobackend
    ```

### Getting Help

If you encounter any issues:

1. Check the [GitHub Issues](https://github.com/Niamorro/audiobackend/issues)
2. Create a new issue with:
    - Your Python version
    - Your operating system
    - The complete error message
    - Steps to reproduce
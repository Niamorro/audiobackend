# Contributing Guide

## Getting Started

### Development Environment

1. Fork and clone the repository:
```bash
git clone https://github.com/your-username/audiobackend.git
cd audiobackend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e .[dev]
```

## Development Workflow

### Making Changes

1. Create a feature branch:
```bash
git checkout -b feature-name
```

2. Make your changes following our guidelines
3. Test your changes:
```bash
pytest
```

### Code Style

We follow a strict code style to maintain consistency:

=== "General Rules"
    - Follow PEP 8
    - Use meaningful variable names
    - Keep functions focused
    - Add type hints
    - Include docstrings

=== "Example"
    ```python
    def process_audio(data: np.ndarray) -> np.ndarray:
        """
        Process audio data with applied effects.
        
        Args:
            data: Input audio array
            
        Returns:
            Processed audio array
        """
        # Your code here
        return processed_data
    ```

### Testing

Write tests for new features:

```python
def test_audio_playback():
    player = AudioBackend()
    assert player.load_file("test.mp3")
    player.play()
    assert player.is_playing
```

Run tests with:
```bash
pytest
pytest --cov=audiobackend  # With coverage
```

### Documentation

Update documentation for changes:

1. Update docstrings
2. Update markdown files in `docs/`
3. Build docs locally:
```bash
mkdocs serve
```

## Pull Requests

### PR Process

1. Update documentation
2. Run tests
3. Create PR with:
    - Clear description
    - Issue references
    - Test results
    - Documentation updates

### PR Template

```markdown
## Description
Brief description of changes

## Related Issues
Fixes #123

## Checklist
- [ ] Tests added
- [ ] Documentation updated
- [ ] Code follows style guide
- [ ] All tests pass
```

## Reporting Issues

### Bug Reports

Include:

1. Python version
2. Operating system
3. Library version
4. Complete error message
5. Minimal reproducible example

### Feature Requests

Include:

1. Use case
2. Proposed solution
3. Example usage

## Project Structure

```
audiobackend/
├── src/
│   └── audiobackend/
│       ├── __init__.py
│       └── audiobackend.py
├── tests/
│   └── test_audiobackend.py
├── docs/
│   ├── index.md
│   └── ...
├── pyproject.toml
└── README.md
```

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Accept feedback

### Enforcement

Violations can be reported to maintainers:

- Via GitHub issues
- Email: niamorrodev@gmail.com

## Getting Help

- Create an issue
- Join discussions
- Read documentation
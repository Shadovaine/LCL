# Contributing to LCL

Thank you for your interest in contributing to the LCL CONTRIBUTION page! We welcome contributions from developers of all skill levels.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:

   ```bash
   git clone https://github.com/ShadoVaine/LCL.git
   cd LCL
   ```

3. Add the upstream repository:

   ```bash
   git remote add upstream https://github.com/ShadoVaine/LCL.git
   ```

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- A Linux environment (or WSL on Windows)
- pipx (recommended) or pip

### Installation

#### Option 1: Using pipx (Recommended for users)

```bash
# Install pipx if you haven't already
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install LCL
pipx install .
```

#### Option 2: Development installation with pip

1. Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

#### Verify installation

```bash
lcl --help
```

## How to Contribute

### Types of Contributions

1. **Bug Reports**: Found a bug? Please report it!
2. **Feature Requests**: Have an idea for a new command or feature?
3. **Code Contributions**: Fix bugs, add features, or improve documentation
4. **Documentation**: Help improve the docs, examples, or tutorials
5. **Command Additions**: Add new Linux commands to the library

### Adding New Commands

When adding a new Linux command:

1. Create a new file in the appropriate category directory
2. Follow the existing command structure:

   ```python
   from core.fields import CommandField
   from core.options import Option
   
   class YourCommand:
       name = "command_name"
       description = "Brief description of what the command does"
       
       options = [
           Option("-o", "--option", "Description of option"),
           # Add more options as needed
       ]
       
       examples = [
           "command_name --option value",
           "command_name -o value"
       ]
   ```

3. Add comprehensive examples and documentation
4. Include both basic and advanced usage examples

## Coding Standards

### Python Style Guide

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise

### Code Formatting

```bash
# Format code with black
black .

# Sort imports with isort
isort .

# Check style with flake8
flake8 .
```

### Documentation

- All new commands must include:
  - Clear description
  - Usage examples
  - Parameter explanations
  - Common use cases

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=lcl

# Run specific test file
python -m pytest tests/test_command_name.py
```

### Writing Tests

- Write tests for all new commands
- Include edge cases and error conditions
- Test both success and failure scenarios
- Use descriptive test names

Example test structure:

```python
def test_command_basic_usage():
    """Test basic command functionality"""
    # Test implementation

def test_command_with_options():
    """Test command with various options"""
    # Test implementation

def test_command_error_handling():
    """Test command error handling"""
    # Test implementation
```

## Submitting Changes

### Before Submitting

1. Ensure all tests pass
2. Update documentation if needed
3. Follow the coding standards
4. Write clear commit messages

### Commit Message Format

```
type(scope): brief description

Longer description if needed

Fixes #issue_number
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

## Issue Guidelines

### Bug Reports

Please include:

- OS and version
- Python version
- LCL version
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)

### Feature Requests

Please include:

- Clear description of the feature
- Use cases and examples
- Why this would be valuable
- Potential implementation ideas

## Pull Request Process

1. **Create a branch** for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Test your changes** thoroughly

4. **Update documentation** if needed

5. **Submit the pull request** with:

   - Clear title and description
   - Reference to related issues
   - Screenshots (if UI changes)
   - Test results

6. **Respond to feedback** and make requested changes

### Pull Request Review Process

- All PRs require at least one review
- Automated tests must pass
- Documentation must be updated for new features
- Code style checks must pass

## Recognition

Contributors will be recognized in:

- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributors section

## Questions?

- Open an issue for questions about contributing
- Check existing issues and discussions
- Reach out to maintainers if needed

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to the Linux Command Library! 🚀

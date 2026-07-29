# Contributing to folder-auto-renamer

Thank you for your interest in contributing to folder-auto-renamer. We welcome contributions from developers of all skill levels.

## Code of Conduct

Please treat all community members with respect and professionalism. Maintain clear, direct, and helpful communication.

## How to Contribute

### Reporting Bugs

Before creating a bug report, check existing issues to ensure the problem has not already been reported.

When submitting a bug report, include:
- A clear description of the issue.
- Operating system version (e.g. Windows 11, Windows 10, Linux, macOS).
- Python version (`python --version`).
- Exact command executed.
- Expected behavior versus actual behavior.
- Relevant log output from `logs/folder-auto-renamer.log`.

### Suggesting Enhancements

Enhancement requests are welcome. Please open an issue detailing:
- The problem your feature solves.
- Proposed CLI flags or behavior changes.
- Why this enhancement would benefit other users.

### Submitting Pull Requests

1. Fork the repository on GitHub.
2. Create a new topic branch off `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your code changes following our standards:
   - Python 3.11+ compatibility.
   - Use only the Python Standard Library. No third-party dependencies.
   - Strictly follow PEP 8 styling conventions.
   - Include Google-style docstrings and clear type hints for all public functions and classes.
   - Do not use emojis in code, comments, docstrings, or commit messages.
4. Run the unit test suite:
   ```bash
   python -m unittest discover -s tests -v
   ```
5. Commit your changes with concise, informative commit messages.
6. Push to your branch and open a Pull Request against `main`.

## Development Setup

Clone the repository and set up a local environment:

```bash
git clone https://github.com/xivamm/folder-auto-renamer.git
cd folder-auto-renamer
python -m venv venv
venv\Scripts\activate
pip install -e .
```

Run test suite:

```bash
python -m unittest discover -s tests -v
```

Thank you for helping improve folder-auto-renamer.

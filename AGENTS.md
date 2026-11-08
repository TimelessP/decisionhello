# Project guidance

- Use Python 3.12 and the workspace `.venv` for development and tests.
- Keep runtime dependencies pinned in `requirements.txt`.
- Use type hints and docstrings for public functions and modules.
- Keep example decisions deterministic in their setup; model answers themselves are probabilistic.
- Never commit API keys, `.env` files, virtual environments, or generated caches.
- Run `python -m unittest discover -s tests -v` after changing application code.
- Rebuild the checked-in sample PNGs with `python scripts/create_examples.py`.

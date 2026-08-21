# Contributing

Bug reports and focused pull requests are welcome. Reproduction cases must use
artificial, non-sensitive text. Changes to validation limits, control-character
handling, focus behavior, or cancellation require tests and an explanation of
their safety impact.

Run the checks locally with:

```bash
python -m pip install -e '.[dev]'
ruff check .
pytest
```

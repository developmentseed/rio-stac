# Contributing

Issues and pull requests are more than welcome.

**dev install**

```bash
$ git clone https://github.com/developmentseed/rio-stac.git
$ cd rio-tiler
$ pip install -e .[dev]
```

**Python3.8 only**

This repo is set to use `pre-commit` to run *isort*, *flake8*, *pydocstring*, *black* ("uncompromising Python code formatter") and mypy when committing new code.

```bash
$ pre-commit install
```

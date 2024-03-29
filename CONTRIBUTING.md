# Contributing

Issues and pull requests are more than welcome.

**dev install**

```bash
$ git clone https://github.com/developmentseed/rio-stac.git
$ cd rio-stac
$ pip install -e .["test","dev"]
```

You can then run the tests with the following command:

```sh
python -m pytest --cov rio_stac --cov-report term-missing
```

**pre-commit**

This repo is set to use `pre-commit` to run *isort*, *flake8*, *pydocstring*, *black* ("uncompromising Python code formatter") and mypy when committing new code.

```bash
$ pre-commit install
```

**Docs**

```bash
$ git clone https://github.com/developmentseed/rio-stac.git
$ cd rio-stac
$ pip install -e .["doc"]
```

Create API docs

```bash
$ pdocs as_markdown --output_dir docs/docs/api/ --exclude_source --overwrite rio_stac.stac
```

Hot-reloading docs:

```bash
$ mkdocs serve
```

To manually deploy docs (note you should never need to do this because Github
Actions deploys automatically for new commits.):

```bash
$ mkdocs gh-deploy -f docs/mkdocs.yml
```

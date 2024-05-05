Development 

How to use uv
`https://github.com/astral-sh/uv`

To create a venv:
```
uv venv 
To install packages:
uv pip install
```

The project uses uv's pip compile to manage the dependencies.

In your venv:
```
uv pip compile requirements.in -o requirements.txt
uv pip install -r requirements.txt
uv pip sync requirements.txt 
```

To upgrade the packages:
`uv pip compile --upgrade requirements.in`

Run pre-commit
`pre-commit install`

update:
`pre-commit autoupdate`

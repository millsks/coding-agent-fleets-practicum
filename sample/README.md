# shelf

A tiny command-line tool for tracking the books on your shelf. It is the sample codebase the practicum's agents work
on: small enough to read in ten minutes, real enough to have bugs, open issues, and tests.

```sh
python -m shelf add "The Pragmatic Programmer" --author "Hunt, Thomas" --year 1999
python -m shelf list
python -m shelf search pragmatic
python -m pytest -q
```

Books are stored in `shelf.json` in the current directory (override with `SHELF_FILE`).

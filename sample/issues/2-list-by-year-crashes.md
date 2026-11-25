# #2 `list --by-year` crashes when a book has no year

**Reported by:** a user · **Labels:** none yet

```
$ python -m shelf add "Untitled notes"
$ python -m shelf list --by-year
TypeError: '<' not supported between instances of 'NoneType' and 'int'
```

The docstring says books without a year go last.

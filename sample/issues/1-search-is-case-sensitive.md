# #1 Search is case-sensitive

**Reported by:** a user · **Labels:** none yet

`python -m shelf search pragmatic` prints "No books found." even though I have *The Pragmatic Programmer* on my
shelf. `search Pragmatic` works. I'd expect search to ignore case for both titles and authors.

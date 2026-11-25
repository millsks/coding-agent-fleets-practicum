# Seeded change for issue #1

`bad-fix.patch` is a plausible-looking but wrong fix for shelf issue #1 ("search is case-sensitive"), the kind an
agent might produce. A good reviewer should block it. Don't read the patch closely before your reviewer has: the point
is to see whether *it* finds the problems.

Apply it in a throwaway git repository made from your workspace:

```sh
cd work/m02-lab1
git init -q && git add -A && git commit -qm base
git apply ../../labs/m02-lab1/seeded/bad-fix.patch
claude -p "Use the reviewer subagent to review the uncommitted changes in this repository." \
  --allowedTools "Read,Grep,Glob,Agent,Bash(git diff *),Bash(git status *)"
git checkout -- . && git clean -fdq   # reset before the next run
```

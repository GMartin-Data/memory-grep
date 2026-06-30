# memgrep

A personal CLI to grep across Claude Code persistent memory.

Claude Code accumulates decisions, feedback, project notes and references in
per-project memory files (`~/.claude/projects/*/memory/*.md`). `memgrep` searches
all of them at once — frontmatter (`name`, `description`) and body — with an
optional `--type` filter and a ripgrep-like output (per-file header, ±2 lines of
context, ANSI highlight when stdout is a TTY).

Single-user, Linux-only. No PyPI, no external dependencies beyond the local repo.

## Install

```sh
uv tool install .
```

Run from the cloned repo. To update after pulling changes:

```sh
git pull && uv tool install --reinstall .
```

## Usage

Search every memory file for a substring (smart-case: case-insensitive when the
pattern is all-lowercase, case-sensitive otherwise):

```sh
memgrep "smart-case"
```

```
/home/you/.claude/projects/memory-grep/memory/decision.md  [name: no case-sensitive flag | type: project]
  3- type: project
  4- ---
  5: v1 keeps smart-case only; no manual case override (YAGNI).

──────────
1 match in 1 file
```

Restrict to one memory type (`user`, `feedback`, `project`, `reference`):

```sh
memgrep --type feedback "stop"
```

Pipe-friendly: when stdout is not a TTY, output is plain (no ANSI colors), so it
composes with other tools:

```sh
memgrep "engineer" | less
```

## Exit codes

| Code | Meaning |
|------|---------|
| `0`  | At least one match found. |
| `1`  | No match (or no memory files to scan) — grep-aligned, empty stdout. |
| `2`  | Environment/usage error: memory directory missing, or invalid `--type`. |

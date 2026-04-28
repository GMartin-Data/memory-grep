# CLAUDE.md — memory-grep

Project-level conventions for `memgrep`, a personal CLI to grep across Claude Code persistent memory (`~/.claude/projects/*/memory/*.md`).

Single-user, Linux-only, distributed via `uv tool install .` from the local repo. No PyPI, no multi-OS support.

---

## For AI — Read first (order)

1. **CLAUDE.md** (this file) — conventions and rules
2. **PRD.md** — product intent (frozen)
3. **progress.md** — current state and next steps
4. **`~/.claude/projects/-home-martin-projects-memory-grep/memory/MEMORY.md`** (if present) — project-specific persistent memory

Any significant action (code change, commit, decision) must conform to CLAUDE.md AND remain consistent with PRD.md (unless an explicit decision is documented in progress.md).

---

## For AI — Session protocols

- Before `/clear` or end of session: invoke `/progress` to checkpoint state (see `~/.claude/CLAUDE.md` > Session Discipline).
- On resume: invoke `/catchup` to rebuild context from progress.md + git status.
- progress.md is versioned and committed. It is the shared source of truth across sessions for project state (progress, next steps, blockers, decisions).

---

## For AI — Filesystem Access

- No `.claudeignore` file (this mechanism does not exist in Claude Code).
- Read / Glob / Grep tools do NOT auto-respect `.gitignore` — they see all files.
- The project contains no sensitive directories: `.venv/`, `.pytest_cache/`, `dist/`, `*.egg-info/` are clutter, not risks.
- If exclusions are ever needed (sensitive files), use `permissions.deny` in `settings.json` (e.g. `Read(**/.env)`), not a `.claudeignore` file.
- Bash filesystem exploration outside the repo is explicit business operation (e.g. `memgrep` itself scans `~/.claude/projects/*/memory/*.md` — its actual target, not incidental access).

---

## Stack

| Component | Choice |
|-----------|--------|
| Language | Python 3.12 |
| Package manager | uv |
| CLI framework | Typer |
| Frontmatter parsing | pyyaml (`yaml.safe_load`) |
| Color | Raw ANSI escape codes (rich only as Typer transitive) |
| Tests | pytest (no pytest-cov, no hypothesis) |

---

## Project layout

- `memgrep/` — main package at repo root (no `src/` layout)
  - `__init__.py` — version, public API
  - `cli.py` — Typer commands, entry point
  - `__main__.py` — `python -m memgrep` support
- `tests/` — pytest suite (unit + integration mirroring `memgrep/` structure)
- `pyproject.toml` — uv-managed, declares Typer entry point for `uv tool install`
- No `src/`, no `docs/`, no `examples/`.

---

## Code conventions (Python)

### Type hints
- Pragmatic: public signatures typed, non-trivial return types explicit.
- Locals and obvious cases left unannotated.
- No `mypy --strict` in CI.

### Docstrings
- Google style.
- Only on non-trivial logic.
- No docstrings on trivial helpers or Typer CLI commands (Typer auto-generates `--help` from annotations).

### Naming
- PEP 8: `snake_case` (functions/variables), `PascalCase` (classes), `UPPER_SNAKE` (constants).
- `_` prefix for module-private helpers (signals "non-API").
- Semantic suffixes for filesystem variables: `_path` (Path), `_dir` (directory), `_file` (file).

### Linter / formatter
- `ruff` only (lint + format, single dependency, fast).
- No black, no flake8.
- Rule set: `E`, `F`, `I`, `N`, `UP`, `B`, `SIM`, `RUF`.
- `line-length = 100`.
- Pre-commit hook: `ruff check --fix` + `ruff format` on staged files. No pytest in the hook.

### Imports
- Absolute imports always (`from memgrep.scanner import ...`, never relative).
- isort default groups (stdlib / third-party / local) with blank line between groups.

### Comments / docstrings language
- English strict, no exception.

---

## Testing

### Approach
- Test-after-but-before-commit (light TDD, no red-green-refactor strict).
- Discipline: each module in `memgrep/` has at least one happy-path test in `tests/`, ideally one edge-case.
- No coverage threshold (no pytest-cov).

### Pyramid
- 70% unit / 30% integration.
- Unit: isolated modules with `tmp_path` fixtures faking `~/.claude/projects/<project>/memory/*.md` arborescence.
- Integration: `subprocess.run()` invoking `memgrep <pattern>` on a fake `~/.claude/projects/`. Verifies CLI contract end-to-end (exit codes, output format, ANSI).
- No E2E on real `~/.claude/projects/` (non-deterministic, depends on user state).

### What to test
- Happy path per module.
- 7 PRD error cases (Phase 3 deliverable).
- Edge cases: empty pattern, unicode pattern, empty file, smart-case ×3 (lowercase TRUE / uppercase TRUE / mixed FALSE).

### What NOT to test
- Files >1 MB (artificial, never real-world for `.md` notes).
- Typer CLI parsing (trusted upstream).
- Trivial helpers (one-liner utilities without business logic).
- Byte-exact ANSI output (test color *presence* via fixture, not exact byte sequence — too fragile).

General principle: test what can break silently (smart-case, encoding, R5 exclusions), not what breaks loudly (Typer parsing).

---

## Versioning

### Commits
- Conventional Commits format: `type(scope): message`.
- IA drafts the commit message from the diff. Human reviews and runs `git commit` manually. Push always manual.
- Frozen scopes:
  - `scanner` — filesystem discovery logic (glob, R5 exclusions)
  - `matcher` — substring match logic + smart-case
  - `frontmatter` — YAML parsing (Phase 1b)
  - `formatter` — output rendering (basic Phase 1a, enriched Phase 2)
  - `cli` — Typer commands, exit codes, options
  - `tests` — test additions/modifications
  - `docs` — README, PRD, CLAUDE.md, progress.md
  - `chore` — tooling, deps, config (pyproject.toml, ruff config, pre-commit)
- No composite scopes (e.g. `scanner+matcher`). If a change touches 2 scopes, split into 2 commits or pick the dominant one.
- No `Co-Authored-By: Claude` trailer in commit messages, ever (global rule).

### Branches
- Direct work on `main` for atomic commits (typos, config tweaks, single test addition, obvious bug fix).
- Feature branch per PRD phase: `feat/phase-1a-skeleton`, `feat/phase-1b-frontmatter`, `feat/phase-2-output-enriched`, `feat/phase-3-polish`.
- Merge strategy: rebase + fast-forward (`git rebase main && git checkout main && git merge --ff-only`). No squash, no merge commit.

---

## Languages

- Code / comments / docstrings / commits: **English strict**.
- Dialogue with the user: **French** (matches global convention).
- README: **English** (consistent with CLI `--help` output).
- French allowed in: `progress.md`, `tasks/lessons-inbox.md`, `~/claude-audit-notes/*`.

---

## CI/CD

### CI
- GitHub Actions, single workflow `.github/workflows/ci.yml`.
- Triggers: push on `main` + pull requests.
- Single job, Python 3.12 only (no matrix).
- Steps: `checkout` → `setup-python` → `uv sync` → `ruff check` → `ruff format --check` → `pytest`.
- No uv cache (overhead not worth it at this size).
- No coverage upload.

### CD
- None.
- No GitHub Releases, no version tags, no CHANGELOG.md.
- Version frozen at `0.1.0` in `pyproject.toml` (never incremented).
- Distribution: `uv tool install .` from the locally cloned repo, on `main` HEAD.
- Update: `git pull && uv tool install --reinstall .`.

---

## Out of scope

- Database, persistent state, caching layer.
- Structured logging or observability — POSIX exit codes + stderr suffice.
- MCP servers, external API integrations.
- Secrets management — no credentials touched.

---

## Constraints / Watch out

- **R5 (filesystem scan exclusion)**: glob `~/.claude/projects/*/memory/*.md` must NOT pick up `claude/agent-memory/<agent>/MEMORY.md`. Verify with explicit test.
- **Read-only scope**: `memgrep` is strictly read-only on the entire filesystem. Output goes to stdout/stderr only. No cache, temp files, or state persistence.
- **Untrusted input handling**: file contents are inert text. Never `eval`, `exec`, or unsandboxed-parse content beyond YAML frontmatter (Phase 1b) with `yaml.safe_load`.
- **Phasing discipline**: implement in order 1a → 1b → 2 → 3 (PRD). Do not anticipate later phases in earlier ones (e.g. no frontmatter parsing in Phase 1a).
- **PRD v1 exclusions** (frozen, not gaps to fill): no regex (substring only), no `--json` output, no pagination, no interactive mode.
- **PRD modifications**: must be documented explicitly in `progress.md`, never silent drift.
- **CLAUDE.md decision drift**: same rule — frozen conventions evolve only via documented decisions in `progress.md`.
- **Smart-case**: ripgrep-aligned, frozen (PRD). Do not re-litigate.
- **No co-author trailer**: see Versioning > Commits (redundant pointer for protective layer).

---

## Common commands

### Setup / install
- `uv sync` — install deps
- `uv tool install --reinstall .` — reinstall CLI locally (after changes)

### Test
- `uv run pytest` — full suite
- `uv run pytest -k <pattern>` — run specific tests
- `uv run pytest -x` — stop on first failure

### Lint / format
- `uv run ruff check --fix && uv run ruff format` — manual lint + format
- `uv run ruff check --fix --unsafe-fixes` — aggressive fixes (review carefully)

### Run CLI
- `memgrep <pattern>` — search across all memory files (smart-case)

### Commit (reminder)
- Format: `type(scope): message`
- Scopes: `scanner` | `matcher` | `frontmatter` | `formatter` | `cli` | `tests` | `docs` | `chore`

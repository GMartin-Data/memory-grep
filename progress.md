## Dernière mise à jour
Date : 2026-04-28 14:30
Session : 49508914-5b77-4e8a-babc-319ea870bd4b

## Tâches complétées
- Repo public GitHub créé (GMartin-Data/memory-grep, SSH, public)
- Interview /claude-md complète (11 phases) — CLAUDE.md projet généré et committé
- uv init : structure package flat (module-root = "" via [tool.uv.build-backend]), Python 3.12
- Phase 1a terminée et mergée sur main :
  - Squelette modulaire : scanner.py, matcher.py, formatter.py, cli.py, __init__.py, __main__.py
  - Smart-case implémenté dès Phase 1a (bonus prévu PRD)
  - Gestion erreurs cas 1, 2, 3 (PRD)
  - 4 smoke tests pytest (subprocess.run + fixture fake_home + tmp_path)
  - uv tool install . validée depuis CWD aléatoire (/tmp)
  - 4 commits sur feat/phase-1a-skeleton, mergés ff-only sur main
- 4 fiches pédagogiques archivées dans ~/claude-audit-notes/ :
  - fiche-ponctuelle-init-vs-main-python-package.md
  - fiche-ponctuelle-cli-integration-testing-subprocess.md
  - fiche-ponctuelle-smoke-test-terminology.md
  - fiche-ponctuelle-rebase-ff-only-workflow.md

## En cours
- Aucune tâche en cours — Phase 1a terminée

## Prochaines étapes
1. Ouvrir une fenêtre de contexte dédiée pour Phase 1b (feat/phase-1b-frontmatter)
2. Phase 1b : ajouter pyyaml (uv add pyyaml), parsing frontmatter (yaml.safe_load),
   match étendu au frontmatter (name, description), flag --type, gestion erreurs cas 6 et 7
3. Valider : `memgrep --type feedback "stop"` filtre correctement
4. Décision en suspens : flag --case-sensitive optionnel pour override smart-case (YAGNI v1 ?)

## Écarts vs PRD
- Smart-case implémenté en Phase 1a (prévu Phase 1b dans le PRD) — avance acceptable,
  cohérent avec l'alignement ripgrep. Pas de dérive fonctionnelle.
- R5 (exclusion agent-memory) non vérifiable empiriquement (aucun dossier agent-memory
  présent sur la machine) — vérification via test tmp_path à prévoir en Phase 1b.

## Décisions prises
- CLAUDE.md projet figé : Python 3.12, uv, Typer, pyyaml, ruff (E/F/I/N/UP/B/SIM/RUF,
  line-length 100), pytest, pre-commit hook (ruff uniquement)
- Scopes Conventional Commits figés (8 scopes : scanner, matcher, frontmatter, formatter,
  cli, tests, docs, chore)
- Branches feature par phase PRD (feat/phase-Nx-<slug>), rebase + ff-only
- Structure flat (memgrep/ à la racine, pas de src/) — module-root = "" dans pyproject.toml
- Smoke tests via subprocess.run + env={"HOME": str(fake_home)} (pas de CliRunner Typer)
- 1 fenêtre de contexte par phase PRD (isolation contexte ↔ feature branch)
- progress.md commité en fin de phase (scope docs)

## Blocages
- Aucun

---

## Dernière mise à jour
Date : 2026-04-27 15:30
Session : c3e5bc40-deb5-4f3f-9cca-689b942e7d71

## Tâches complétées
- Interview PRD complète (13 phases, 3 blocs de validation)
- PRD.md généré et verrouillé
- Smart-case acté dans PRD.md (post-interview, alignement ripgrep)
- Repo git initialisé (`git init`)

## En cours
- Aucune tâche en cours — PRD finalisé, prêt à démarrer l'implémentation

## Prochaines étapes
1. Créer CLAUDE.md projet via `/claude-md` (figer conventions Python 3.12 + uv + Typer + pyyaml)
2. Trancher le flag `--case-sensitive` optionnel pour override smart-case (YAGNI v1 ?)
3. Démarrer Phase 1a : `uv init`, squelette Typer, scan `~/.claude/projects/*/memory/*.md`, match contenu, smoke test, install locale
4. Vérifier en Phase 1a que le glob exclut bien `claude/agent-memory/<agent>/MEMORY.md` (R5)

## Écarts vs PRD
- Aucun

## Décisions prises
- Substring littérale (pas regex v1) — regex reporté v2
- Smart-case style ripgrep (insensible si pattern tout-minuscule, sensible sinon)
- Scan multi-projets `~/.claude/projects/*/memory/*.md` (pas limité au projet courant)
- Highlight ANSI conditionnel TTY — pas de colorama (Linux only)
- pyyaml pour frontmatter, ANSI brut (rich seulement si Typer l'embarque déjà)
- Install via `uv tool install .`, pas de PyPI
- Exit codes : 2 pour erreur d'environnement (dossier absent), 1 pour "rien trouvé" (alignement grep)
- Cas 4 (frontmatter malformé) : warning stderr non silencieux + scan contenu
- 4 phases d'implémentation : 1a (squelette), 1b (frontmatter + filtre), 2 (output enrichi), 3 (polish)
- 8 critères de succès binaires/mesurables (dont 5a stabilité + 5b utilité, et perf <1s)

## Blocages
- Aucun

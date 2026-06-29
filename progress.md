## Dernière mise à jour
Date : 2026-06-29 12:40
Session : d8586491-f904-4a04-a59c-04ea6c32be5a

## Tâches complétées
- feat/phase-1b-frontmatter mergée ff-only sur main puis poussée (origin d2035a5..5ab30b6)
  - checkpoint Phase 1b commité sur la branche avant merge (scope docs)
  - branche locale + distante supprimées (nettoyage post-phase)

## Prochaines étapes
1. Ouvrir une fenêtre de contexte dédiée pour Phase 2 (feat/phase-2-output-enriched)
2. Phase 2 : header par fichier, contexte ±2 lignes, highlight ANSI conditionnel TTY,
   résumé final "N matches dans M fichiers", vérification cas 5 (fichier illisible)

## Décisions prises
- --case-sensitive REJETÉ en v1 (YAGNI). On garde le smart-case seul (ripgrep-aligned,
  figé PRD). Pas d'override manuel de la casse : si pattern tout-minuscule → insensible,
  point. Le point ouvert reporté depuis Phase 1a est donc clos. Réévaluable en v2 si un
  besoin réel de distinguer `stop` de `Stop` émerge.

---

## Dernière mise à jour
Date : 2026-06-25 18:00
Session : 712752d3-551a-4c51-ab3c-cd688ae0b781

## Tâches complétées
- Mise en adéquation méthodologique (workflow changé depuis création du projet) :
  - ADR-0011 créé dans ~/dotfiles/adr/ : critères qualitatifs du "track léger"
    (mono-utilisateur, pas de collaborateurs, pas de distribution publique,
    durée de vie non-critique → exempté de PLAN.md et d'ADRs)
  - Renvoi une-ligne ajouté dans responsibility-matrix.md (découvrabilité)
  - CLAUDE.md projet : note d'application track léger + renvoi ADR-0011
  - PRD.md : note d'en-tête historique (gelé, précède doctrine actuelle)
  - Bug de regex consigné dans ~/dotfiles/TODO.md :
    block-force-push.sh matche -f dans les noms de branche (ex: "frontmatter")
  - Mémoire persistante initialisée : light-documentary-track.md + MEMORY.md
- Phase 1b terminée et poussée sur feat/phase-1b-frontmatter (3 commits) :
  - feat(frontmatter) : parse_frontmatter() — parsing YAML, fallbacks cas 4/7,
    InvalidFrontmatterError pour YAML malformé / délimiteur manquant / non-mapping
  - feat(cli) : option --type user|feedback|project|reference — validation cas 6
    (exit 2 + message), filtre-avant, warning stderr cas 4
  - tests : 5 tests unitaires frontmatter + 6 tests d'intégration --type
  - 14/14 tests verts, zéro régression Phase 1a
  - Validation PRD manuelle : `memgrep --type feedback "stop"` filtre correctement
  - Revue /code-review xhigh : zéro bug de correctness confirmé

## En cours
- Aucune tâche en cours — Phase 1b terminée, branche poussée

## Prochaines étapes
1. Rebase + merge ff-only de feat/phase-1b-frontmatter sur main
2. Ouvrir une fenêtre de contexte dédiée pour Phase 2 (feat/phase-2-output-enriched)
3. Phase 2 : header par fichier (<path> + [name: X | type: Y]), contexte ±2 lignes,
   highlight ANSI conditionnel TTY, résumé final "N matches dans M fichiers",
   gestion erreurs cas 5 (fichier illisible — déjà câblé, à vérifier)
4. Décision à confirmer avant Phase 2 : --case-sensitive YAGNI (reporté depuis 1a)

## Écarts vs PRD
- Smart-case implémenté en Phase 1a (prévu Phase 1b) — avance assumée, cohérent
  avec l'alignement ripgrep. Pas de dérive fonctionnelle.
- Cas 4 (warning frontmatter malformé) câblé en Phase 1b (prévu Phase 2) —
  avance assumée : frontmatter.py levait déjà InvalidFrontmatterError, ne pas la
  câbler aurait laissé une exception non gérée. Comportement conforme PRD.
- R5 (exclusion agent-memory) : test de non-régression non ajouté (aucun dossier
  agent-memory présent sur la machine, vérification par construction du glob
  documentée dans scanner.py). Toujours à couvrir via test tmp_path en Phase 2/3.
- PLAN.md absent : décision assumée (track léger, cf. ADR-0011 dotfiles).
- Décision en suspens reportée : flag --case-sensitive YAGNI v1 — à trancher
  avant Phase 2 (pas de changement de code impliqué).

## Décisions prises
- Track léger : projet exempté de PLAN.md et d'ADR (cf. ADR-0011 dotfiles,
  note dans CLAUDE.md). Décisions durables consignées ici, pas en ADR.
- --type filtre avant scan (sémantique naturelle).
- Match frontmatter = ligne YAML comme match (vrai numéro de ligne dans le fichier
  source), pas sélection fichier entier. Scan sur content complet maintenu.
- --type exact-match (sensible à la casse) : le smart-case s'applique au pattern
  de recherche, pas au filtre de métadonnée. Convention : les 4 types sont en
  minuscules par doctrine ~/.claude/CLAUDE.md.
- Type non-string (ex: type: 123) ou type absent sous --type → exclusion silencieuse
  (pas de warning). Outil perso, frontière interne, pas un cas réel attendu.
- Contournement bug hook block-force-push.sh : utiliser `git push` nu (upstream
  préconfiguré) pour les branches contenant "-f" dans le nom.

## Blocages
- Aucun

---

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

# PRD — memgrep

## Résumé

La mémoire persistante de Claude Code (`~/.claude/projects/*/memory/*.md`) accumule au fil des sessions des décisions, des retours utilisateur, des notes projet et des références externes. Sans outil de recherche, ce capital devient inutilisable en pratique : on redécouvre des choses déjà résolues, ou on ouvre plusieurs fichiers à la main pour retrouver une information.

`memgrep` est une CLI standalone qui résout ce problème par une recherche full-text substring sur l'ensemble de la mémoire — frontmatter (name + description) et contenu — avec filtre optionnel par type de mémoire et un rendu ripgrep-like (header par fichier, contexte ±2 lignes, highlight ANSI conditionnel TTY).

L'outil est strictement personnel, sans dépendance externe ni packaging public, installé via `uv tool install .` depuis le repo.

## Problème

Au fil des sessions Claude Code, des informations utiles s'accumulent dans la mémoire persistante : règles de comportement validées (feedbacks), profil utilisateur, contexte projet, pointeurs vers des systèmes externes. Cette mémoire est organisée en fichiers `.md` séparés avec frontmatter (`name`, `description`, `type`).

Sans outil de recherche dédié, il est impossible de mobiliser ce capital efficacement :
- pas de recherche full-text sur l'ensemble des fichiers,
- pas de filtre par type de mémoire (`user`, `feedback`, `project`, `reference`),
- pas de visibilité sur le contexte autour d'un match.

Conséquence concrète : on redécouvre des décisions déjà prises, ou on ouvre 5 fichiers à la main pour retrouver un retour donné des semaines plus tôt.

## Solution

Une CLI Python `memgrep <pattern>` qui scanne `~/.claude/projects/*/memory/*.md`, applique une recherche substring littérale sur le frontmatter et le contenu, propose un filtre `--type` aligné sur les 4 types de mémoire, et produit un rendu ripgrep-like avec contexte, highlight ANSI conditionnel TTY et résumé final.

## Utilisateurs cibles

Usage personnel uniquement (un seul utilisateur, sur sa propre machine Linux). Overhead minimal : pas de doc utilisateur public, pas de packaging PyPI, pas de support multi-OS.

## User Stories

- En tant qu'utilisateur Claude Code, je veux chercher un mot-clé dans toute ma mémoire persistante, afin de retrouver instantanément une décision ou un feedback déjà capturé sans ouvrir 5 fichiers.
- En tant qu'utilisateur, je veux filtrer la recherche par type de mémoire (`--type feedback`), afin d'isoler par exemple tous les feedbacks que j'ai donnés à Claude sans le bruit des notes projet ou références.
- En tant qu'utilisateur, je veux que la recherche couvre à la fois le titre/description (frontmatter) et le contenu des mémoires et m'affiche le chemin du fichier + un extrait de contexte, afin de juger la pertinence d'un résultat sans avoir à ouvrir le fichier.

## Fonctionnalités v1

### Recherche
- ✅ Substring littérale avec **smart-case** (alignement ripgrep) : insensible à la casse si le pattern est tout en minuscules, sensible sinon
- ✅ Scan de `~/.claude/projects/*/memory/*.md`
- ✅ Couverture frontmatter (`name`, `description`) + contenu
- ✅ Filtre `--type user|feedback|project|reference`

### Output
- ✅ Header par fichier : chemin complet + ligne `[name: <name> | type: <type>]`
- ✅ Lignes matchées préfixées par numéro de ligne, contexte ±2 lignes
- ✅ Highlight ANSI du pattern dans l'extrait si TTY détecté
- ✅ Plain text non-coloré si stdout n'est pas un TTY (piping)
- ✅ Résumé final `N matches dans M fichiers` séparé par une barre

## Périmètre v1

| ✅ Inclus | ❌ Exclu (v2+) |
|-----------|----------------|
| Substring littérale frontmatter + contenu | Recherche regex |
| Filtre `--type` sur les 4 types | Recherche fuzzy / typo tolerance |
| Output ripgrep-like (header, contexte ±2) | Indexation persistante / cache |
| Highlight ANSI conditionnel TTY | Support des `MEMORY.md` d'agents (`claude/agent-memory/<agent>/`) |
| Scan multi-projets `~/.claude/projects/*/memory/*.md` | TUI interactif |
| Résumé final N matches / M fichiers | Intégration Claude Code (slash command, MCP) |
|  | Pipe-friendly mode (`--no-color`, JSON) |

## Stack technique

| Composant | Choix | Justification |
|-----------|-------|---------------|
| Langage | Python 3.12 | Cohérent avec convention utilisateur (uv comme package manager) |
| Package manager | uv | Convention utilisateur globale |
| CLI | Typer | Typage natif, autocomplétion shell gratuite, doctrine FastAPI-like familière |
| Couleur ANSI | Codes ANSI bruts (ou `rich` si Typer l'embarque déjà) | Linux-only, pas besoin de `colorama` (wrapper Windows inutile) |
| Parsing frontmatter | pyyaml | Standard, suffisant pour le format `--- ... ---` simple |
| Dépendances externes | Aucune | Lecture filesystem locale uniquement |
| Authentification | Aucune | Mémoire locale |
| Déploiement | `uv tool install .` depuis le repo | Pas de PyPI, pas de Docker, binaire local |

## Format de sortie

Format ripgrep-like :

```
<chemin-fichier>
[name: <frontmatter.name> | type: <frontmatter.type>]
<lineno>: <extrait>
  ...avec ±2 lignes de contexte

<chemin-fichier-suivant>
...

──────────
N matches dans M fichiers
```

Règles :
- Header par fichier : chemin complet + métadonnées extraites du frontmatter (`name`, `type`).
- Lignes matchées préfixées par numéro de ligne, contexte ±2 lignes autour.
- Highlight ANSI du pattern dans l'extrait si TTY détecté.
- Plain text non-coloré si stdout n'est pas un TTY (pour piping).
- Résumé final séparé par une barre horizontale.

## Gestion des erreurs

| # | Cas d'erreur | Comportement |
|---|--------------|--------------|
| 1 | Le dossier `~/.claude/projects/` est introuvable (problème d'environnement) | Message stderr `No memory directory found at <path>`. Exit code **2**. |
| 2 | Aucun fichier `.md` trouvé dans les dossiers scannés | Sortie `0 matches dans 0 fichiers`. Exit code **1** (alignement strict avec `grep`). |
| 3 | Aucun match pour le pattern (mais des fichiers scannés) | Sortie `0 matches dans 0 fichiers`. Exit code **1**. |
| 4 | Frontmatter YAML malformé dans un fichier | Warning sur stderr `<path>: invalid frontmatter, scanning content only`, puis scan du contenu. |
| 5 | Fichier illisible (perms, lien cassé) | Warning sur stderr `<path>: cannot read (<reason>)`, skip et continue. |
| 6 | Valeur `--type` invalide | Message listant les valeurs admises (`user`, `feedback`, `project`, `reference`). Exit code **2**. |
| 7 | Fichier sans frontmatter du tout | Pas une erreur — scan du contenu brut, header affiché sans la ligne `[name: ... | type: ...]`. |

## Phases d'implémentation

### Phase 1a : Squelette + scan minimal
**Objectif :** avoir une commande `memgrep <pattern>` qui retourne des résultats lisibles, sans frontmatter ni filtre.
**Livrables :**
- ✅ `pyproject.toml` (uv) + arborescence `memgrep/__init__.py`, `memgrep/cli.py`, `memgrep/__main__.py`
- ✅ CLI Typer avec arg `pattern` seul
- ✅ Scan de `~/.claude/projects/*/memory/*.md`
- ✅ Match substring sur le **contenu** uniquement (pas encore de frontmatter)
- ✅ Output basique `<path>:<lineno>:<line>` (style grep simple, sans contexte)
- ✅ Install `uv tool install .` testée localement
- ✅ Squelette `pytest` avec 1 test smoke
- ✅ Gestion erreurs cas 1, 2, 3

**Validation :** `memgrep "feedback"` retourne des résultats depuis n'importe quel CWD.

### Phase 1b : Frontmatter + filtre type
**Objectif :** étendre le matching et activer le filtrage par type.
**Livrables :**
- ✅ Parsing frontmatter via pyyaml
- ✅ Match substring étendu au frontmatter (`name`, `description`)
- ✅ Flag `--type user|feedback|project|reference`
- ✅ Gestion erreurs cas 6 et 7

**Validation :** `memgrep --type feedback "stop"` filtre correctement.

### Phase 2 : Output ripgrep-like enrichi
**Objectif :** passer du format minimal au rendu cible.
**Livrables :**
- ✅ Header par fichier : `<path>` + `[name: X | type: Y]`
- ✅ Contexte ±2 lignes autour de chaque match
- ✅ Highlight ANSI conditionnel TTY (`sys.stdout.isatty()`)
- ✅ Résumé final `N matches dans M fichiers` séparé par barre
- ✅ Gestion erreurs cas 4 et 5 (warnings stderr non silencieux)

**Validation :** sortie conforme à la maquette du format de sortie, identique TTY/non-TTY (sans couleurs en pipe).

### Phase 3 : Polish
**Objectif :** robustesse et confort d'usage minimal.
**Livrables :**
- ✅ README minimal (install + 2-3 exemples d'usage)
- ✅ `--help` Typer propre (descriptions arg + flag)
- ✅ Étoffement de la suite de tests : couverture des 7 cas d'erreur

**Validation :** README en place, `--help` propre, tests automatisés couvrant les cas 1 à 7. (Le critère de dogfooding est évalué dans la section Critères de succès, pas ici.)

## Risques & Mitigations

| # | Risque | Impact | Mitigation |
|---|--------|--------|------------|
| R1 | Dérive de la convention frontmatter au fil du temps (la convention `name`/`description`/`type` est définie par l'utilisateur dans son `~/.claude/CLAUDE.md`, pas par Anthropic). | Moyen — résultats trompeurs sans crash. | Lecture défensive : si une clé attendue manque, fallback gracieux (cas 7). Tests de régression sur des exemples réels. |
| R2 | Volume de mémoire qui grossit dans le temps, scan complet à chaque appel devient lent. | Faible v1, croissant. | Acceptation explicite v1 (pas d'indexation). Mesuré par le critère de succès performance ; si seuil franchi en dogfooding, déclenchement de la décision d'indexation v2. |
| R3 | Glob multi-projets ramasse des chemins inattendus (dossier `memory/` dans un projet utilisateur indexé par Claude). | Faible — pollution résultats. | Acceptation v1 (pollution statistiquement faible). Si observé en dogfooding, ajouter un flag `--paths` pour restreindre (v2). |
| R4 | Substring naïve trop bruyante sur patterns courts (`memgrep "user"` ramène trop de matches). | Moyen — outil moins utile en pratique. | Pas de mitigation v1 (regex/fuzzy reportés). Pousser vers patterns plus longs. À surveiller en dogfooding. |
| R5 | Inclusion non-désirée des `MEMORY.md` d'agents (`claude/agent-memory/<agent>/MEMORY.md` est explicitement hors scope v1). | Faible — pollution résultats. | Vérification explicite en Phase 1a que le glob `~/.claude/projects/*/memory/*.md` les exclut. Affinement du glob si nécessaire. |

## Critères de succès

8 critères binaires/mesurables :

- ✅ **1. Couverture fonctionnelle** — `memgrep <pattern>` et `memgrep --type <type> <pattern>` retournent des résultats corrects sur les 4 types de mémoire (`user`, `feedback`, `project`, `reference`).
- ✅ **2. Format de sortie conforme** — la sortie correspond strictement à la maquette (header, métadonnées frontmatter, contexte ±2, séparateur, résumé final), avec ANSI conditionnel TTY.
- ✅ **3. Couverture des 7 cas d'erreur** — chaque cas a un test automatisé qui vérifie le bon exit code et le bon message stderr/stdout.
- ✅ **4. Install reproductible** — `uv tool install .` depuis le repo produit une commande `memgrep` invocable depuis n'importe quel CWD.
- ✅ **5a. Stabilité** — `memgrep` ne crashe pas et ne produit pas de résultats incorrects sur 1 semaine d'usage quotidien.
- ✅ **5b. Utilité validée** — au moins 5 fois pendant cette semaine, `memgrep` a évité d'ouvrir manuellement plusieurs fichiers mémoire (compteur subjectif via mini-journal d'usage).
- ✅ **6. Performance** — sur la volumétrie de mémoire au moment du test (à dater), `memgrep "<pattern à matches multiples>"` renvoie en moins de **1 seconde**. Si le seuil est franchi en dogfooding, déclenche la décision d'indexation v2 (mitigation R2).
- ✅ **7. Périmètre validé** — `memgrep` ne scanne pas `claude/agent-memory/<agent>/MEMORY.md` (vérifié par test manuel ou par inspection sur un pattern uniquement présent dans ces fichiers exclus).

## Évolutions futures (v2+)

- Recherche regex
- Recherche fuzzy / typo tolerance
- Indexation persistante / cache (déclenchée si critère perf 6 franchi)
- Support des `MEMORY.md` d'agents
- TUI interactif (fzf-like)
- Intégration Claude Code (slash command, MCP server)
- Pipe-friendly mode (`--no-color`, format JSON)
- Flag `--paths` pour restreindre le glob (déclenché si R3 observé en dogfooding)

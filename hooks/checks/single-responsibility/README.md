# Single-responsibility check

A unit has one reason to change when it talks to one external entity. This check
counts the distinct external entities each callable, class and module reaches.
**Two or more entities blocks the commit**: two entities are two reasons to change,
so the unit is split.

`hooks/pre-commit` runs it after file length. It analyzes all current Python,
TypeScript, TSX, MTS and CTS files under the services' declared `src` directories,
including untracked and unstaged files. It never imports or executes application
code and does not use the network or an AI service. `./install.sh` installs
everything needed and enables the hooks.

```sh
hooks/checks/single-responsibility/check

# Every unit, its entities and the calls that establish them:
.venv/bin/python hooks/checks/single-responsibility/srp_check.py \
  --json user-service/src content-management-service/src \
  ui-service/src api-gateway/src

# Individual files or directories are also accepted:
.venv/bin/python hooks/checks/single-responsibility/srp_check.py path/to/file.py
```

## What counts as an external entity

An entity is one **kind of outside world**, identified from resolved library
operations. The supported entities are:

| Entity | Recognized from |
|---|---|
| `ai` | model provider clients |
| `authentication` | token, signature, password and hashing libraries |
| `email` | mail transport libraries |
| `filesystem` | file and directory operations |
| `network` | HTTP, socket and object-storage clients |
| `persistence` | database, ORM, cache and web-storage clients |
| `presentation` | template engines and DOM rendering |
| `process` | subprocess and child-process execution |
| `queue` | brokers and task queues |

The catalogue lives in [srp_effect_rules.py](srp_effect_rules.py) as
`(entity, module prefixes, operation names)`. A call is an entity only when both
the resolved module prefix and the operation name match. Nothing is inferred from
a name alone: `database.save` on an unresolved object is not persistence, and an
unknown package is never guessed.

Deliberately **not** entities, because they are vocabulary rather than an
independently owned policy: value types and stdlib helpers, the web framework,
local modules, sibling components, logging, serialization and path manipulation.
This keeps the rule general — it depends on resolved library identity, never on
directory layout, service names or project vocabulary.

## Counting

`entities = distinct entities reached`, and
`coefficient = min(1, 0.25 * entities)`. The threshold is **0.5**, compared
inclusively, so the gate is exactly two entities:

| Entities | Coefficient | Result |
|---:|---:|---|
| 0 | 0.00 | pass |
| 1 | 0.25 | pass |
| 2 | 0.50 | **block** |
| 3 | 0.75 | **block** |
| 4 or more | 1.00 | **block** |

Repeating one entity is never a second reason to change: four `httpx` calls are
one entity. Exit codes: `0` below threshold, `1` findings, `2` analysis error.
The shell wrapper also exits nonzero for missing tooling. Parse and read errors
cannot turn into a successful partial report.

**Callables** count the entities they reach directly plus the entities reached
through uniquely resolved helper calls. A coordinator that calls a downloader and
a writer reaches both entities; it does not inherit the helpers' size.
Referencing a helper without calling it adds nothing. Duplicate or observably
reassigned definitions are excluded.

**Classes and modules** count the union of their members' entities. A module of
two single-entity functions still has two reasons to change, and the report names
which member reaches each entity.

Entity identity survives re-exports and aliases: two wrappers for one operation
are one operation, and a local module named like a library is distinguished from
that library when its source is in the scan. Explicit dependency types are
resolved so injected clients are visible, including Python `Annotated`, nullable
unions, string annotations and type aliases, TypeScript nullable types and
aliases, typed local variables and class fields, and TypeScript parameter
properties. Type metadata is never evaluated.

The file and repository coefficient is the **maximum unwhitelisted** unit value,
so clean files cannot dilute a finding. Overlapping inputs, relative and absolute
spellings and symbolic links to the same file are deduplicated.

## Use in another codebase

The engine accepts arbitrary source files and directories and has no dependency
on this repository's service names, frameworks or vocabulary. Copy this directory
to another project, or invoke it by absolute path. The shell `check` wrapper is
the integration with this repository's hooks.

Run it with Python 3.12 or newer, using a version that can parse the target
syntax. TypeScript analysis additionally needs Node and an installed TypeScript
compiler; it uses that compiler's parser and module resolver, looked up in the
scanned projects' `node_modules`, then in this repository's hook tooling.
`--typescript` and `--node` override those choices. The regression suite uses
Python 3.12 and TypeScript 5.9.

```sh
python /tools/single-responsibility/srp_check.py --json /project

python /tools/single-responsibility/srp_check.py --json \
  --source-root /project/backend \
  --typescript /tools/node_modules/typescript \
  --tsconfig /project/frontend/tsconfig.app.json \
  /project/backend /project/frontend
```

Python roots are inferred from `src`, project metadata (`pyproject.toml`,
`setup.cfg`, `setup.py`), package `__init__.py` files, or the supplied scan
directories. Repeat `--source-root` for independent import roots in a monorepo.
TypeScript uses the nearest `tsconfig.json`, including `extends`, `baseUrl` and
`paths`, or an explicit `--tsconfig`. Without a config it uses TypeScript's Node
module resolution. Resolving imports never executes their code.

Adopting the check in a project that uses libraries outside the catalogue means
adding those `(entity, prefixes, operations)` rows. Absence of a row is absence
of evidence, not proof of compliance.

## Review findings and whitelist false positives

The check tells the agent to first identify whether each finding is a real
violation, and to split only those. A finding that is not a real violation is
never refactored — whitelist it instead: add that exact finding and a concrete
reason to [whitelist.txt](whitelist.txt) beside this check. The file starts with
no active exceptions. It accepts one JSON object per line, with blank lines and
`#` comments allowed:

```json
{"path":"src/example.py","kind":"module","name":"<module>","reason":"Why these entities are one reason to change."}
```

Copy `kind` and `name` from the JSON report. Paths are relative to the command's
working directory, which is the repository root for the hook; absolute paths also
work. Matching uses the exact physical file, kind and unit name. Wildcards are
not supported, and an exception never exempts another finding in the same file.
Revisit exceptions when the code changes. Invalid entries, missing reasons and
duplicate findings fail the analysis.

Standalone users may pass `--whitelist /project/whitelist.txt`; the default is the
file beside this checker. JSON keeps every unit's original coefficient and
evidence, adds `whitelist_reason` to matches, and reports `whitelisted_count`.
Only whitelisted units are excluded from the blocking maximum.

## Report

Schema version 6. Each file carries its units and `source_root`; each unit
carries `entities`, `coefficient`, `kind`, `name`, `line`, `whitelisted`,
`effect_domains` with the exact calls, `direct_effect_domains` and
`delegated_effect_domains` separately, and `reasons`. Owners additionally carry
`entity_members`, naming which member reaches each entity. Callable `metrics`
retain the raw AST facts — size, statements, complexity, nesting, parameters,
locals, calls, resolved call aliases, links and per-statement flow — as
explanation of a finding. They do not affect the verdict. Coefficients are
normalized to twelve decimal places before the inclusive comparison.

## Limits

Library coverage is explicit. Unresolved wrappers, dynamic imports, computed
`require`, dynamic `module.exports`, Python wildcard re-exports, reflection,
complex aliases and indirect operations may be missed, and re-export traversal is
bounded to 64 steps. Binding analysis is an approximation, including block scopes
and comprehensions. Inherited fields reached through `self`/`this` are visible,
but inherited method bodies are not resolved across files. Only files supplied to
the scan contribute helper bodies.

Two independently changeable policies that reach the same entity — or no entity
at all — are invisible to this rule. A composition root that only wires modules
reaches no entity and correctly passes. Genuinely cohesive work that crosses two
media, such as writing a temporary file in order to run a converter, is reported
and is a legitimate whitelist candidate after review.

An entity count is a deliberately blunt, explainable reading of "one reason to
change". It is not a calibrated probability, and the literature does not validate
this rule. Absence of a finding does not establish compliance. See
[the research report](RESEARCH.md) and [the evaluation](EVALUATION.md).

## Verification

```sh
.venv/bin/pytest -q hooks/tests/test_srp_*.py
```

Tests cover the entity count and its properties, the inclusive two-entity
boundary, every supported entity, repeated operations, delegation through local,
nested, imported, re-exported, transitive and recursive helpers, uncalled and
shadowed and reassigned and duplicate helpers, owner unions and member
attribution, dependency injection through annotated, nullable, aliased and
constructor-assigned types, library-name collisions, namespace and package
layouts, tsconfig inheritance and path aliases, default, star and CommonJS import
forms, ambiguous re-exports and cycles, paths with spaces, overlapping input
spellings, syntax errors, missing tooling, deterministic JSON, whitelist matching
and its failure modes, and execution of a copied checker outside this repository.
These are regression tests, not an accuracy benchmark.

# Single-responsibility check

`hooks/pre-commit` runs this check after file length. It analyzes all current
Python, TypeScript, TSX, MTS and CTS files under the services' declared `src` directories,
including untracked/unstaged files, as the other architecture checks do. This
is a working-tree check, not a snapshot of only the Git index. It never imports
or executes application code and does not use the network or an AI service.
The existing `./install.sh` installs everything needed and enables the hooks.

```sh
hooks/checks/single-responsibility/check

# Detailed, machine-readable scores, including those below the threshold:
.venv/bin/python hooks/checks/single-responsibility/srp_check.py \
  --json user-service/src content-management-service/src \
  ui-service/src api-gateway/src

# Individual files or directories are also accepted:
.venv/bin/python hooks/checks/single-responsibility/srp_check.py path/to/file.py
```

## Use in another codebase

The standalone engine accepts arbitrary source files/directories and has no
dependency on this repository's service names, frameworks or business vocabulary.
Copy this entire check directory to another project, or invoke it by absolute
path. The shell `check` wrapper is the integration with this repository's hooks.

Run the analyzer with Python 3.12 or newer, using a Python version that can parse
the target source syntax. TypeScript analysis additionally needs Node and an
installed TypeScript compiler; it uses that compiler's parser and module resolver.
It looks for TypeScript in the scanned projects' `node_modules`, then in this
repository's hook tooling. `--typescript` and `--node` override those choices.
The regression suite uses Python 3.12 and TypeScript 5.9.

```sh
python /tools/single-responsibility/srp_check.py --json /project

# Namespace packages, selected individual files, or a custom TypeScript config:
python /tools/single-responsibility/srp_check.py --json \
  --source-root /project/backend \
  --typescript /tools/node_modules/typescript \
  --tsconfig /project/frontend/tsconfig.app.json \
  /project/backend /project/frontend
```

Python roots are inferred from `src`, project metadata (`pyproject.toml`,
`setup.cfg`, `setup.py`), package `__init__.py` files, or the supplied scan
directories. Repeat `--source-root` to specify independent import roots in a
monorepo. TypeScript uses the nearest `tsconfig.json`, including `extends`,
`baseUrl` and `paths`, or an explicit `--tsconfig`. Without a config it uses
TypeScript's Node module resolution. Explicitly resolved TypeScript imports can
cross package boundaries when both files are in the scan. The scan only scores
the supplied source files; resolving imports never executes their code.

The coefficient is in **[0, 1]**. An unwhitelisted score **>= 0.5** blocks the commit,
including exactly 0.5. Exit codes: `0` below threshold, `1` SRP findings, `2` analysis
error. The shell wrapper also exits nonzero for missing tooling. Parse/read
errors cannot turn into a successful partial report. JSON includes each
callable/class/module, its location, raw metrics, normalized signals and
reasons. JSON includes caller populations, missing evidence,
effect-slice lines, workflow counterevidence, the God Class conjunction,
per-file source roots, selected TypeScript configs and original-to-resolved
call aliases. JSON has separate `direct_effect_domains` and
`delegated_effect_domains`; `effect_domains` includes both. Each statement's
`callees` identifies resolved helper paths/names, and `delegated_effects` records
their possible operations. Schema version 5 also includes `whitelisted`, the
review reason for each exception, and file/repository `raw_coefficient` values.
The file and repository coefficient is the **maximum unwhitelisted** unit score: unrelated
clean files cannot dilute a finding. Adding callers can legitimately change
the evidence, so analyze complete source trees for the most useful result.
Overlapping inputs, relative/absolute spellings and symbolic links to the same
source file are deduplicated. Each physical file contributes only one client;
the report retains the first input spelling encountered for that file.

This is an explainable heuristic, **not a calibrated probability or proof**.
Zero means no evidence under these rules; one means maximal modeled evidence.
Neither endpoint establishes business intent. SRP concerns reasons for change,
which cannot be established from static syntax alone. Accuracy has not been
measured against a representative, human-labelled SRP dataset for this repo.

## Review findings and whitelist false positives

The check tells the agent to first identify whether each finding is a real
violation. Fix only the real ones. A finding that is not a real violation is
never refactored - whitelist it instead: add that exact finding and a concrete
reason to [whitelist.txt](whitelist.txt) beside this check.
The file starts with no active exceptions. It accepts one JSON object per line,
with blank lines and `#` comments allowed:

```json
{"path":"src/example.py","kind":"module","name":"<module>","reason":"Explain why these groups have one reason to change."}
```

Copy `kind` and `name` from the JSON report. Paths are relative to the command's
working directory, which is the repository root for the hook; absolute paths
also work. Matching uses the exact physical file, kind and unit name. It does
not support wildcard exceptions or exempt other findings in the same file.
Revisit exceptions when the corresponding code changes. Invalid entries,
missing reasons and duplicate findings fail the analysis.

Standalone users may pass `--whitelist /project/whitelist.txt`; the default is
the file beside this checker. JSON retains every unit's original coefficient
and evidence, adds `whitelist_reason` to matches, and reports `whitelisted_count`.
Only whitelisted units are excluded from the blocking maximum.

The 0.5 cutoff is a stricter review policy. Score formulas and the 0.8
high-confidence boundary retain their previous values. Moderate scores,
including some focused workflows, can now interrupt a commit for review.

## Signals and scoring

Method length counts source lines occupied by runtime AST nodes/tokens; blank
lines, comments, Python docstrings, annotations and nested callable bodies do
not inflate the enclosing method. This is an executable-line approximation,
not physical file length. Nested functions, arrows, lambdas, async functions
and methods receive their own scores. The independent 200-line file limit
continues to apply.

Each structural metric is normalized with
`ramp(x, a, b) = max(0, min(1, (x-a)/(b-a)))`:

| Metric | Zero through | Maximum at | Burden weight |
|---|---:|---:|---:|
| Executable method lines | 25 | 80 | 0.25 |
| Statements | 15 | 50 | 0.20 |
| Cyclomatic complexity approximation | 4 | 15 | 0.20 |
| Control-flow nesting | 2 | 5 | 0.10 |
| Distinct calls (fan-out) | 4 | 12 | 0.10 |
| Parameters (excluding receiver) | 4 | 9 | 0.075 |
| Local variables | 6 | 18 | 0.075 |

`B` is the weighted sum. Recognized library operations are grouped into
filesystem, network, persistence, process and presentation concerns. A strong
concern requires two distinct resolved calls; repeating one call does not
strengthen it. Import aliases and simple assignments in functions and at module
scope are resolved. Assignment right-hand sides are analyzed before replacing
the previous binding. Unbound or shadowed names, including Python exception and
pattern captures, are not guessed to be libraries. Logging, constructors,
serialization and path manipulation alone are not classified as I/O.

Explicit dependency types include Python `Annotated`, nullable unions, string
annotations and type aliases; TypeScript nullable types and aliases; and typed
local variables and class fields. Straight-line constructor assignments can
establish field dependencies, including TypeScript parameter properties. An
inferred field type is discarded if another path can replace it; explicit type
annotations are trusted. Conflicting union alternatives provide no positive
type evidence. Type metadata is never evaluated.

Explicit type/library re-exports preserve operation identity across files.
Local modules with library-like names are distinguished from the external
libraries when their source is included. Actual calls to uniquely resolved local
or imported helpers carry summaries of the helpers' possible I/O operations.
This includes named nested functions, TypeScript arrow/function expressions,
class methods, local function aliases,
re-exports and transitive/recursive calls. Referencing a helper without calling
it does not add I/O evidence. Duplicate or observably reassigned definitions
are excluded from summaries. Only files supplied to the scan contribute bodies.

Summaries preserve the original library operation identities: two wrappers for
the same operation do not count as two operations. The caller keeps its own
line count, statement count, complexity and fan-out; helper body size is never
added to its burden. A small coordinator remains below the high-confidence band;
its moderate score can still reach the stricter 0.5 gate.

Callable score: `0.65 * min(1, strong_concerns/2) + 0.35 * B`.
It is capped at 0.79 unless all three conditions hold:

- At least two strong concerns.
- At least two structural signals >= 0.5.
- At least two independent, substantial effect slices.

The slices track statement-level reads/writes back to earlier definitions.
Each supported domain requires two distinct operations and at least four
contributing top-level statements. Domains are connected when one consumes
another's effect result, or their slices overlap by at least 50% of the smaller
slice. Connected domains form one workflow group. This is conservative AST
provenance, not a full control-flow/program-dependence graph. Compound statements
are grouped, and receiver calls may mutate their receiver. Unrelated padding
cannot supply missing slice support. Shared workflow evidence caps the score.
Delegated effects enter the slice at the actual calling statement. Return values,
arguments and shared receivers can connect those calls into a workflow; all
effects reached through a single call share that event. This is not full
interprocedural data flow: hidden global state and argument mutation inside
helpers are not comprehensively modeled.

For classes/modules, methods form a graph using shared fields, imported
dependencies, module globals and internal method calls. Constructors are
excluded from cohesion so initializing every field does not connect unrelated
behavior. Short helpers remain in the graph. A supported component contains
at least two methods with two or more statements, at least six statements in
total, and observed state/dependency usage **or a resolved call between members
of that component**. This also makes independent pure calculation groups
measurable. An unconnected collection of pure helpers is still insufficient.
Callback parameters, bare calls from methods, and calls on other objects cannot
supply internal-method evidence merely by sharing a method's name.

Let `D = 1 - largest_component_size/member_count`,
`S = min(1, smallest_supported_component_statement_count/12)` and `Bmax` be the
largest member burden. Set `S=0` with fewer than two supported components.
The review score is `0.40 * min(1, 2*D) + 0.15*S + 0.10*Bmax`.
Without measurable resource relationships, only `0.10*Bmax` remains; missing
data is not treated as proven cohesion. A supported disconnected partition can
reach the stricter 0.5 gate without reaching high confidence.

Additional research-informed measurements:

- Tight/loose cohesion: pairwise shared field access, including fields reached
  through internal calls, and connectivity through other methods. These are
  TCC/LCC-inspired **runtime-member variants**: private helpers are included,
  constructors excluded. They are diagnostic, not extra copies of the same
  evidence added to the score.
- Normalized disconnected component count, inspired by YALCOM. The graph here
  also includes imports/globals. Unmeasurable metrics are `null` in JSON.
- External-effect profile similarity (Jaccard overlap). Separate I/O concerns
  include delegated operations, so separation can remain visible despite a
  shared helper module or shared entity fields. Each supported effect group
  must have two nontrivial methods, twelve of those methods' own statements
  and two distinct resolved operations. With at least two such groups, the
  alternate review score is `0.50 + 0.15*(1 - mean_similarity) + 0.10*Bmax`;
  the owner takes the maximum of the review scores, not their sum.

Reaching the high-confidence band (>= 0.8) requires additional evidence from at
least one of these routes:

- **Segregated clients:** a supported component/effect partition has at least
  two observed client source files per group and no client shared between
  groups. Raise its score to at least `0.8 + 0.10*Bmax`. Explicit imports,
  aliases, module-level calls and internal wrappers contribute caller evidence.
  Each source file is one client, not each method. Clients propagate through
  internal calls and resolved cross-file wrappers. A shared client prevents
  that partition from qualifying and subtracts 0.05 from the review score.
  Missing or ambiguous targets cannot supply positive evidence.
- **God Class conjunction:** for classes only, approximate weighted method
  count >= 47, more than 5 distinct foreign-data references, and measurable
  tight field cohesion < 1/3. Raise the score to at least
  `0.8 + 0.10*ramp(weighted_methods,47,100) + 0.10*(1-tight_cohesion)`.
  All three must hold. These are runtime AST proxies, not PMD's Java metrics.

Caller resolution uses the selected/inferred Python import roots and TypeScript
compiler resolution. Supported forms include Python absolute/relative imports
and explicit re-export aliases; TypeScript named/default exports, export aliases,
star re-exports, path aliases, static `require`/`import = require` and `export =`.
Flat object destructuring of explicit module bindings is supported. Re-export
cycles and ambiguous targets cannot supply positive evidence. Compiler-resolved
precedence, such as `.ts` before `.tsx`, is honored. A single-file scan normally lacks client context;
`insufficient_evidence`/`null` makes that visible. Source files are only a proxy
for actors: separate clients do not prove independent business ownership.

Coefficients are normalized to twelve decimal places before the inclusive
threshold comparison. Weights, support requirements and thresholds above are
local engineering choices; the cited papers do not validate this formula.

## Research and limits

See [the research report](RESEARCH.md) for primary sources, implementation
decisions, the original false-positive analysis and a calibration plan. The
research led to caller corroboration, workflow counterevidence and a
PMD-inspired conjunctive God Class rule. None of the papers validates the local
coefficient formula. Full program slicing, lexical topic models, Git co-change
history and learned/LLM classification remain outside the hook.

Limitations: library coverage is explicit in `srp_effects.py`; unresolved wrappers,
dynamic imports, computed `require`, dynamic `module.exports`, Python wildcard
re-exports, reflection, complex aliases and indirect I/O may be missed. Binding
and control-flow analysis remain approximations, including block scopes and
comprehensions. Re-export traversal is bounded to 64 steps. Unsupported or
unresolved constructs do not establish compliance.
Top-level executable statements contribute client references but are not
individually scored as callables. Inherited fields accessed through `self`/`this`
are visible, but inherited method bodies are not resolved across files.
Shared logging/state may hide separate components. Pure computational SRP
violations may lack observable effects, clients or foreign state. Conservative
flow merging can miss unrelated work inside a single control-flow block.
Genuine orchestration and related adapters can still score highly. Inspect
reported groups in context; absence of a flag does not establish compliance.
Lowering a coefficient is not evidence that a refactoring improved the design.

## Verification

See [the detection and portability comparison](EVALUATION.md) for the before/after
regression results and their limits.

```sh
.venv/bin/pytest -q hooks/tests/test_srp_*.py
```

Tests cover score bounds and monotonic size contributions, the inclusive 0.5
boundary, mixed/focused behavior, aliases and shadowing, transitive/static
cohesion, separate external concerns sharing state, nested scopes, syntax
errors, deterministic JSON, source scope, paths with spaces and missing tools.
They also cover module-level client instances, reassignment evaluation order,
Python exception/pattern captures, overlapping source paths, mixed path spellings,
pure calculation groups and their counterexamples, dependency injection,
nullable/annotated/aliased types, library-name collisions, portable package layouts,
compiler config inheritance, default/re-export/CommonJS import forms,
and execution of a copied checker outside this repository. They also cover
independent versus shared computation, irrelevant padding,
caller segregation/shared callers, relative imports, source-tree isolation,
ambiguous resolution, typed foreign-data access, the three-way God Class
condition and a reconstructed combined-adapter finding under its original and
a different filename. The separated adapters pass the stricter gate. Whitelist
tests verify exact matching, retained evidence, unsuppressed findings, malformed
entries and the agent instructions. These are regression tests, not an accuracy benchmark.

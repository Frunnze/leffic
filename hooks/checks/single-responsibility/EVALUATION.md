# Detection and portability regression comparison

## Current policy and extractor split

The commit threshold is now **0.5**, with score calculations unchanged. Before
the split, the combined `link_extractor.py` module was the only repository
finding at this cutoff, scoring `0.509261363636`. It now has separate
`youtube_transcript.py` and `webpage_extractor.py` modules, coordinated by
`text_sources.py`. The 201-file scan passes at `0.408333333333`, with no active
whitelist exceptions. The extraction and text-source tests pass (57 tests).

The historical comparison tables below used the previous **0.8** gate. Their
Pass/Block expectations refer to that policy; they do not describe the stricter
current cutoff. Exact false positives can now be documented in `whitelist.txt`
after review, while preserving their raw scores and evidence in JSON.

## Original detection comparison

Compared the checker snapshot at the start of this improvement (127 passing
SRP tests) with the updated checker on 16 generated source projects. Both
versions received the same project files, Python interpreter, TypeScript
compiler and unchanged inclusive 0.8 blocking threshold.

The baseline missed 8 expected blocking cases and blocked 1 expected passing
case. The updated checker matched the expected outcome in all 16 cases.
These are synthetic regression scenarios with expectations derived from the
documented detection policy. They are not an independently human-labelled
business-responsibility dataset and do not establish general precision,
recall, or calibration across real projects.

| Scenario | Expected | Before | After |
|---|---|---:|---:|
| Python: independent pure calculation groups | Block | 0.0000 | 0.8000 |
| Python: calculation groups with a shared client | Pass | 0.0000 | 0.4250 |
| Python: independent direct I/O implementations | Block | 0.8998 | 0.8998 |
| Python: one I/O concern | Pass | 0.5660 | 0.5660 |
| TypeScript: independent pure calculation groups | Block | 0.0000 | 0.8000 |
| TypeScript: calculation groups with a shared client | Pass | 0.0000 | 0.4250 |
| TypeScript: independent direct I/O implementations | Block | 0.8954 | 0.8954 |
| TypeScript: one I/O concern | Pass | 0.5660 | 0.5660 |
| Python: Annotated dependency | Block | 0.5748 | 0.8998 |
| Python: local module named httpx | Pass | 0.8998 | 0.5748 |
| Python: class re-exported through a package | Block | 0.4750 | 0.8000 |
| TypeScript: constructor-injected dependency | Block | 0.5704 | 0.8954 |
| TypeScript: default-exported class | Block | 0.4750 | 0.8000 |
| TypeScript: configured module path alias | Block | 0.4750 | 0.8000 |
| Python: imported dependency type, independent work | Block | 0.5748 | 0.8998 |
| Python: imported dependency type, shared workflow | Pass | 0.5748 | 0.7900 |

Scores are rounded for display; decisions use twelve decimal places.

## Helper-call follow-up

Compared the 204-test snapshot with the helper-summary implementation on 18
additional generated projects, using the same interpreter/compiler and 0.8
threshold. This table scores the target callable or class; a coordinator's
implementation helper can have its own separate finding. Each row was run in
both Python and TypeScript, with the same displayed scores in both languages.

| Target scenario (Python and TypeScript each) | Expected | Before | After |
|---|---|---:|---:|
| Independent jobs through local helpers | Block | 0.2410 | 0.8910 |
| Helper return value feeds the next helper | Pass | 0.2410 | 0.7900 |
| Independent jobs through imported helpers | Block | 0.2410 | 0.8910 |
| Independent jobs through nested helpers | Block | 0.2410 | 0.8910 |
| Class method calls separate module helpers | Block | 0.2410 | 0.8910 |
| Small coordinator calls a complex implementation | Pass | 0.0000 | 0.6500 |
| Original helper bindings reassigned to pure functions | Pass | 0.2410 | 0.2410 |
| Shared helper module, separate owner client populations | Block | 0.0000 | 0.8000 |
| Shared helper module, a client uses both groups | Pass | 0.0000 | 0.5500 |

All 10 previously missed target findings are detected; all 8 expected passing
targets remain below threshold. These remain synthetic policy regressions,
with the same accuracy limitations as the first comparison.

## Coverage beyond the comparison

The full SRP suite now passes 278 tests. The additional tests exercise
Python packages and namespaces without src directories, explicit import
roots, nullable and forward-reference types, type aliases, constructor
injection, mutable-field counterexamples, TypeScript .mts/.cts and runtime
extension mapping, inherited and explicit tsconfig files, named/default/star
re-exports, default-arrow wrappers, static CommonJS imports, ambiguous exports,
cycles, shadowed imports and callbacks, and local library-name collisions.
Helper regressions add transitive/recursive I/O summaries, nested and member
calls, local aliases, arrow and named function expressions, uncalled references,
reassigned/duplicate definitions, operation deduplication, caller burden
isolation, shared receiver workflows and segregated/shared owner clients.
Current policy tests cover the inclusive 0.5 boundary, the extractor split, and
exact whitelist entries with reasons, retained evidence and error handling.

A test copies the entire checker into an unrelated temporary project and
runs it using that project's TypeScript installation. This verifies that
the standalone engine works independently of the repository hook wrapper.

The 201-file repository scan passes with coefficient 0.408333333333 at threshold 0.5.
Python lint/format checks and JavaScript/shell syntax checks also pass.

Run the regression suite:

```sh
.venv/bin/pytest -q hooks/tests/test_srp_*.py
```

The scenarios are covered by test_srp_computation.py, test_srp_types.py,
test_srp_projects.py, test_srp_portability.py, test_srp_delegation*.py and the
existing scoring/flow tests. See the README for standalone usage and remaining
analysis limits.

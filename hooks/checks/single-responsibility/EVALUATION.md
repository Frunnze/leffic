# Evaluation

## What the previous implementation did on this repository

The coefficient blended implementation burden, disconnected member components,
client populations, effect-slice workflows and a God Class conjunction. Scanning
the four declared source trees produced:

| Measurement | Value |
|---|---:|
| Units scored | 1,283 |
| Units scoring exactly `0.0` | 1,200 |
| Highest unit score | `0.4025` |
| Units at or above the `0.5` gate | 0 |
| Callables reaching the two effect domains the formula required | 0 of 969 |
| Callables with observable effect flow | 0 of 969 |
| Units with a measurable `tight_cohesion` | 0 |

Nothing could block, and the ranking was not meaningful. The three
highest-scoring units were a 17-line module of two functions, a 3-function
prompt-loading module and a file of Solid event handlers — all scoring `0.4`
because their members share no state. `json.ts`, with eleven unconnected members,
scored `0.0`, because the separation term required at least one member to touch
an import and none did.

## What the entity rule does on this repository

Same four source trees, same working-tree scan:

| Measurement | Value |
|---|---:|
| Files analyzed | 203 |
| Units scored | 1,286 |
| Units reaching 0 entities | 969 |
| Units reaching 1 entity | 277 |
| Units reaching 2 entities | 34 |
| Units reaching 3 entities | 4 |
| Units reaching 4 entities | 2 |
| **Blocking findings** | **40** (3.1%) |
| Distinct files with a finding | 12 |

Findings by kind: 30 callables, 9 modules, 1 class. By service:
content-management 19, user-service 11, ui-service 10. Entities observed across
the scan: persistence 157, network 137, authentication 42, process 13,
filesystem 12, ai 4.

### The findings

| Entities | Unit |
|---:|---|
| 4 | `study_units_generation/extraction_router.py` module and `extract_text` — filesystem, network, persistence, process |
| 3 | `file_upload/file_uploader.py` module and `get_file` — filesystem, persistence, process |
| 3 | `extraction_router._extracted_text` — filesystem, network, process |
| 3 | `study_units_generation/text_sources.py` module — filesystem, network, process |
| 2 | `generation_router.py` and four of its callables — authentication, persistence |
| 2 | `task_status_router.py` and `_owned_task_id` — authentication, persistence |
| 2 | `text_sources` file readers, `file_uploader._converted_to_pdf`, `shared/pdf_conversion.PdfConversion` — filesystem, process |
| 2 | `assessment/AssessmentReview.tsx`, six callables — network, persistence |

Spot-checking the evidence:

- `generate_study_units` — `hmac.new`, `hmac.new.hexdigest` and six distinct
  SQLAlchemy session operations. Task-signing policy and storage policy change
  for different reasons. Real.
- `AssessmentReview` — `global.fetch` and `global.localStorage.getItem`. Real.
- `PdfConversion.converted` — `tempfile.TemporaryDirectory` and `subprocess.run`.
  One job by any reasonable reading, two entities by this rule. This is the
  intended whitelist case.

The whitelist starts empty; no finding is suppressed by default.

## Detection comparison

Both implementations on the same fixtures, same interpreter and compiler:

| Scenario | Previous | Entity rule |
|---|---|---|
| 17-line module, two unrelated pure functions | `0.4000` | `0.0000` pass |
| 11 unconnected pure helpers, no imports | `0.0000` | `0.0000` pass |
| Function calling `httpx` and `pathlib` | blocks on burden | blocks, 2 entities |
| Function calling `httpx` four times | `0.5660` blocks | `0.2500` pass |
| Network result written to disk (one workflow) | capped below gate | blocks, 2 entities |
| Small coordinator over a downloader and a writer | `0.6500` | blocks, 2 entities |
| Class whose methods each reach one distinct entity | needed 2 clients each | blocks, 2 entities |
| Composition root wiring modules, no operations | `0.4000` on separation | `0.0000` pass |
| Injected `httpx.Client` through `Annotated`/nullable/alias | `0.8998` | blocks, 2 entities |
| Local module named `httpx` | `0.5748` | pass, not the library |
| Unknown package with `write` and `send` | `0.0000` | `0.0000` pass |

Two deliberate reversals are visible. A long function with one concern no longer
blocks: length is the file-length check's business. A chained network-to-disk
pipeline now does block: the previous workflow guard treated it as one
responsibility, and under this rule it is two.

These are policy regressions on fixtures written for the policy. They are not a
precision or recall measurement against human-labelled SRP violations, and none
has been performed. See [the research report](RESEARCH.md) for what the
literature does and does not support.

## Suite

```sh
.venv/bin/pytest -q hooks/tests/test_srp_*.py
```

225 tests pass at this revision. Four test modules covering removed evidence
families — member-component cohesion, client segregation, effect-slice workflows
and independent pure-computation groups — were deleted with the code they tested.
`test_srp_entities.py` covers the rule itself, including four Hypothesis
properties: entities are unique and sorted, unresolved names never become
entities, the coefficient never decreases as entities are added and stays in
`[0, 1]`, and it crosses the threshold exactly at two entities.

The remaining modules retain their coverage of the machinery the rule still
depends on: Python and TypeScript adapters, import roots and namespace layouts,
tsconfig inheritance and path aliases, default, star and CommonJS import forms,
re-export cycles and ambiguity, dependency-type resolution, helper delegation
across files and scopes, paths with spaces, overlapping input spellings, missing
tooling, deterministic JSON and the whitelist.

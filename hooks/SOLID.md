# SOLID coverage in the pre-commit gate

What each principle is enforced by today, and what is left to a reviewer.

| Principle | Enforced? | How | Gap |
| --- | --- | --- | --- |
| **S** — Single Responsibility | Partly | `10-file-length` (≤200 lines, `.py`/`.ts`/`.tsx`), `17-class-methods` (≤4 methods per class), `15-definition-names` (no `_and_` / `And` in a name), `16-nested-definitions`, `18-duplicate-code`, ruff `PLR0904` | All proxies for size, not for responsibility. A 200-line file can still do three jobs and a 4-method class can still have two reasons to change. |
| **O** — Open/Closed | **No** | — | Nothing stops a growing `if kind == "a" / elif kind == "b"` chain. Candidate check: flag a function comparing one subject to 3+ string literals. Measured **0 violations** today, so it would land free. |
| **L** — Liskov Substitution | Partly | `30-basedpyright` with `typeCheckingMode = "all"`: `reportIncompatibleMethodOverride` rejects an override that narrows its parameters or widens its return type; `reportImplicitOverride` forces every override to be marked `@override` | An override whose body is only `raise NotImplementedError` passes (refused bequest). Candidate check: `@override` present, `@abstractmethod` absent, body is a lone `raise NotImplementedError`. Measured **0 violations**. Behavioural substitution (the Square/Rectangle case) is undecidable and will never be checked. |
| **I** — Interface Segregation | Barely | `17-class-methods` caps every class at 4 methods, which incidentally caps ABCs and Protocols | No rule aimed at interfaces. Candidate check: cap `ABC`/`Protocol` methods at 3. Measured **0 violations** — the widest is `AIManager` at 2. |
| **D** — Dependency Inversion | **No** | `13-feature-isolation` keeps sibling features apart, which is modularity, not inversion | Nothing stops a feature importing concrete infrastructure. Measured: 15 imports across 10 files name a vendor — `requests`, `bs4`, `youtube_transcript_api`, `celery`, `openai`, `pika`, `pypdf`, `textract`, `fsrs`, `cryptography`, `jwt`. A check was written and then dropped: enforcing it pushes single-consumer adapters into `shared/`, which currently means "used by more than one feature". Enforcing D needs a home for infrastructure that is *not* shared — a per-feature `adapters/` package or a top-level `src/adapters/` — decided before the check, not after. `sqlalchemy` in 17 feature files is `Session` annotations; treating those as violations means a repository layer, a larger decision again. |

## Reading this table

Three of the gaps (O, the refused-bequest half of L, and I) measure **zero violations** today. They are ratchets: adding them locks in the current state at no cleanup cost. D is the only one that needs work first — six files to move.

None of these prove a principle holds. They detect the smells that usually accompany a violation, which is the same thing the existing `S` checks do.

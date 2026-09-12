# Principles and the checks that enforce them

The software engineering principles this repository commits to, the checks in
this folder that enforce each one, and how well those checks hold the line.
Ranked from the best enforced to the least.

- **High** - a violation is mechanically detected and blocks the commit.
- **Medium** - the common shapes are caught; a determined violation slips past.
- **Low** - only a narrow symptom is caught, or nothing is.

| Principle | Checks enforcing it | Enforcement |
| --- | --- | --- |
| Single Responsibility Principle | `single-responsibility` (SRP coefficient >= 0.5 blocks), `file-length` (max 300 lines), `definition-names` (no `and`/`or` in a name), `nested-definitions` | High |
| YAGNI | `dead-code` (vulture), `unused-deps` (deptry, knip), `feature-isolation` (shared needs two owners) | High |
| Type safety - make illegal states unrepresentable | `strict-typing` (basedpyright `typeCheckingMode = "all"`, `npm run typecheck`), `linters` (eslint `strictTypeChecked`) | High |
| Modularity - high cohesion, low coupling | `feature-isolation` (siblings meet only in `shared`), `file-length`, `single-responsibility` | High |
| Explicit dependencies | `unused-deps` (declare what you import, drop what you don't) | High |
| Separation of config from code (Twelve-Factor III) | `secrets` (gitleaks over the staged diff) | High |
| Testability - every unit reachable and exercised | `property-tests` (one `test_<function>_property_<guarantee>` per definition), `coverage` (100% branch, shuffled), `nested-definitions` | High |
| Robustness against untrusted input | `api-contract` (generated requests must not crash an endpoint), `security-patterns` (semgrep dataflow) | High |
| Readability over cleverness | `linters` (ruff 79-column lines, import order, naming, no lambda bindings; pylint; eslint) | High |
| Consistency - one obvious way to express a thing | `linters` (ruff `RET` returns, `FBT` flag arguments, `E711`/`E721` identity and type tests, `B006` mutable defaults) | High |
| Secure by default | `vulnerable-deps` (pip-audit, npm audit), `security-patterns`, `secrets` | High |
| Open/Closed Principle | `open-closed` (variant dispatches, closed factories, registries, protocol strings) | Medium |
| Liskov Substitution Principle | `strict-typing` (override compatibility), `linters` (pylint `arguments-differ`, `signature-differs`, `invalid-overridden-method`) | Medium |
| Dependency Inversion Principle | `dependency-inversion` (collaborators constructed instead of injected) | Medium |
| DRY | `duplicate-code` (jscpd), `linters` (pylint `duplicate-code`) | Medium |
| KISS | `linters` (ruff complexity, argument and statement limits), `file-length`, `single-responsibility` | Medium |
| Fail fast - reject invalid state at the first judge | `api-contract`, `linters` (ruff `S`, `TRY`, `S101` bans `assert` for validation) | Medium |
| Error transparency - never swallow a failure | `linters` (ruff `BLE001`, `S110`, `TRY` family) | Medium |
| Resource safety - scoped acquisition and release | `linters` (ruff `SIM115`, pylint `confusing-with-statement`) | Medium |
| Test-first development | `coverage` (a branch no test asked for fails), `property-tests` | Medium |
| Design by Contract | `property-tests` (enforces the property exists and is generated over, not that it asserts a guarantee) | Medium |
| Immutability by default | `linters` (ruff `B006`, `RUF012`) | Medium |
| Interface Segregation Principle | `linters` (ruff `max-public-methods = 15`), `dependency-inversion` | Low |
| Information hiding / encapsulation | `linters` (ruff `SLF001` private access) | Low |
| Intention-revealing naming | `definition-names` (catches only joined `and`/`or` names), `linters` (ruff `N`, pylint `disallowed-name`) | Low |
| Short functions - one screen, one job | `linters` (ruff `PLR0915`, limit 50 statements against the 20-line rule) | Low |
| Self-documenting code (no explanatory prose) | `linters` (ruff `ERA001` catches commented-out code only) | Low |
| Principle of Least Astonishment | `linters`, `api-contract` | Low |
| Command-Query Separation | none | Low |
| Composition over inheritance | none | Low |
| Law of Demeter | none | Low |
| Avoid premature optimization | none | Low |
| Caller owns its data - no surprise mutation | none | Low |
| Boy Scout Rule - leave it cleaner | none | Low |
| Traceable, human-authored history | none (no commit-msg hook: message shape and AI attribution are unchecked) | Low |
| Observability through dedicated logging seams | none | Low |

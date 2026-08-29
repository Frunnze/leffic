# Production To-Dos — Leffic

What stands between this repo and a public deployment, in the order it
should be done. Every item names the file that carries the problem, so it
can be checked rather than believed.

**Verdict:** not deployable today. A clean checkout cannot build the
frontend, authenticated users can place or extract files outside their own
folders, test sessions are not scoped to an owner, and the current quality
gate is red.

Grouped by tier. P0 blocks any exposure at all; P1 blocks a public launch;
P2 is what makes it survivable in the long run.

---

## P0 — the app does not work when built

- [x] **A clean checkout now builds the frontend image.** `ui-service`
  standardised on npm: `ui-service/package-lock.json` is tracked, the
  `package-lock.json` rule left the root `.gitignore`, and the stale
  `ui-service/pnpm-lock.yaml` was deleted. `api-gateway/package-lock.json`
  and `hooks/package-lock.json` are tracked too, both regenerated so the
  lock records the `overrides` their `package.json` declares. A new
  `tracked-lockfiles` pre-commit check runs first and fails the commit if
  any declared npm package has no lockfile in `git ls-files`. Verified: a
  `git archive HEAD ui-service` extracted into an empty directory and
  built with `docker build` exits 0, with `ui-service/.dockerignore`
  keeping `node_modules`, `dist`, `tests` and `.DS_Store` out of the
  context.
- [x] **The gateway image is not reproducible.** `api-gateway/Dockerfile`
  runs `npm install` rather than `npm ci`, so every build resolves the
  dependency tree afresh and can drift from the tree that was tested. Now
  that `api-gateway/package-lock.json` is tracked, copy it into the build
  stage and switch to `npm ci`.
- [x] **The production bundle now points at the real gateway.**
  `ui-service/Dockerfile` takes `ARG VITE_GATEWAY_URL` / `ENV
  VITE_GATEWAY_URL` before `npm run build`, and `docker-compose.yml` passes
  it as a build arg defaulting to `http://localhost:8888` for local runs, so
  `shared/api/session.ts` no longer falls back to a localhost origin that
  every other machine resolves to itself. Verified: a build with
  `VITE_GATEWAY_URL=https://api.example.test` carries that origin in
  `dist/assets/` and no `localhost:8888` anywhere. The value ships in the
  bundle, so it must be the externally reachable origin, not a service name.
- [x] **Deep links and refresh now resolve.** `ui-service/nginx.conf` serves
  `/usr/share/nginx/html` with `try_files $uri $uri/ /index.html;` and the
  Dockerfile copies it to `/etc/nginx/conf.d/default.conf`, so `/login`,
  `/folder/home`, `/settings` and `/note/:id` survive a reload instead of
  404ing against the stock `nginx:alpine` config.
- [x] **Alembic now owns both database schemas.** Each Python service has
  its own configuration and initial revision under `migrations/`, application
  startup no longer calls `Base.metadata.create_all`, and Compose runs the
  `user-migrations` and `content-migrations` jobs before starting anything
  that uses those databases. Migration tests cover upgrade, model parity,
  a single revision head and downgrade for both services.

## P0 — broken access control

The gateway verifies the JWT before proxying protected routes and both
services verify it again in `shared/claims_extractor.py`. No service port is
published directly by `docker-compose.yml`; keep it that way. A `user_id`
claim that is not a UUID is refused with 401 instead of reaching the database
and failing as a 500. The remaining problems happen *after* authentication:
several endpoints still do not establish ownership of the row they act on.

- [x] **Deleting content now proves ownership.** `delete_deck`,
  `delete_test`, `delete_note` and `delete_file`
  (`features/file_system/content_router.py`) and `delete_folder`
  (`folder_router.py`) take `AuthenticatedUserId` and resolve the row
  through `shared/content_access.py`, `shared/file_access.py` or
  `shared/folder_access.py`, which join `Folder` and filter `Folder.user_id`.
  A foreign id, an unknown id and a non-UUID id all answer 404 with the same
  body, so none of them confirms a row exists. Deleting your own home folder
  is 422 `Home folder cannot be deleted!`, checked after ownership so a
  foreign home folder still answers 404. `create-folder` checks its parent
  too — a folder planted in another learner's tree used to be destroyed,
  with its notes and files, by that learner's next delete cascade.
- [x] **Reading study material now proves ownership.** `get_note`
  (`note_router.py`), `get_flashcards?flashcard_deck_id=`
  (`flashcard_router.py`) and `get_test_items?test_id=`
  (`assessment_router.py`) resolve the note, deck or test through the same
  owner-scoped lookup before any child row is read, so a container owned by
  someone else is 404 rather than an empty list. `get_test_items` checks
  before it opens a `TestSession`, so a refused read leaves no session row
  behind.
- [x] **Listing a folder now proves ownership.** `access_folder`
  (`folder_router.py`) scoped its name lookup to the caller, and `_notes`
  in `folder_contents.py` gained the `Folder.user_id` filter its four
  sibling queries already had — without it, `access-folder` handed a
  foreign folder's name *and* every note inside it to any logged-in caller.
  A folder owned by someone else now reads exactly like an unknown one.
- [x] **Generating into a folder now proves ownership.**
  `generate_study_units` (`generation_router.py`) resolves the target
  through `owned_folder_id`, so study units can no longer be written into
  another learner's folder. `study_unit_writer._owned_folder` was renamed
  `_existing_folder`, since it never checked an owner and its name claimed
  a guarantee the code did not provide.
- [x] **A malformed folder id is 404, not 500.** `resolved_folder_id` and
  `owned_folder_id` (`shared/folder_access.py`) parse the id before it
  reaches the `FlexibleUuid` bind, so `create-folder`, `move-unit`,
  `notes-stats`, `flashcards-stats` and the folder read paths answer 404
  instead of raising out of the database layer.
- [x] **A non-dict task result is no longer a 500.** `_finished_result`
  (`task_status_router.py`) substitutes the `FAILURE` status instead of
  raising `TypeError` when a succeeded task's `result` is not a dict, so
  `flashcards-status`, `test-task-status` and `note-task-status` answer
  `200 {"status": "FAILURE"}` — byte-identical to a genuinely failed
  task — where an owner whose own task returned a non-dict used to get a
  500.
- [x] **`GET /file` now proves ownership.** `get_file`
  (`features/file_upload/file_uploader.py`) takes `AuthenticatedUserId`
  and resolves the id through `owned_file`
  (`features/file_system/file_access.py`) before it reads anything off
  disk — the same lookup the bookmark endpoints in that feature already
  routed through. A foreign or unknown file id now answers 404 instead
  of streaming the file.
- [~] **The task-status endpoints prove ownership, but the branch is not
  green yet.**
  `generate_study_units` (`generation_router.py`) no longer hands back a
  bare Celery id: `note_task_id`, every `flashcard_task_ids` entry and
  every `test_task_ids` entry is now `signed_task_id(task_id, folder_id)`
  from `features/study_units_generation/task_ownership.py`, an
  HMAC-SHA256 token `<task_id>.<folder_id>.<hexdigest>` signed with the
  service's `SECRET_KEY` under its own domain prefix so a JWT signature
  can never be replayed as a task token. `get_flashcard_status`,
  `get_test_task_status` and `get_note_task_status`
  (`task_status_router.py`) each take `AuthenticatedUserId`, run the path
  parameter through `verified_task_id` — a `hmac.compare_digest`
  check — and then `owned_folder` on the embedded folder id, before any
  Celery or database read. A forged or tampered digest, a token signed
  for a folder that does not exist, another learner's well-signed token,
  a malformed reference such as `a.b.zzz` and a raw Celery uuid all
  answer the identical 404 `{"detail": "Task does not exist!"}` on all
  three routes, so none of them confirms a task exists. Verified: a token
  the caller minted still answers `{"status": "PENDING"}` and the
  succeeded-task bodies keep every key they had; the five refusal shapes
  were compared body-for-body across the three routes; and `ui-service`
  needed no change, since it only ever echoes the ids it was given. The
  repository gate still reports three `fast-api-unused-path-parameter`
  errors, and four property tests call the handlers with the old `task_id`,
  `user_id`, `db` signature and fail. Reconcile the dependency/handler
  signature and make the full gate green before marking this complete.
- [x] **Uploading a file does not prove folder ownership.** `upload_files`
  (`features/file_upload/file_uploader.py`) calls `resolved_folder_id`, which
  only parses the id, then `_recorded_files` loads `Folder` by id without a
  `user_id` predicate. Any authenticated learner can therefore attach a
  document to another learner's folder. Resolve the folder with
  `owned_folder_id` before writing bytes, and remove partial files if either
  storage or the database operation fails.
- [x] **Text extraction bypasses file ownership and accepts storage paths.**
  `ExtractionRequest.file_metadata` carries arbitrary `file_id` and
  `extension` strings; `text_from_files` (`text_sources.py`) concatenates
  them into `files/{file_id}.{extension}` and reads the path with no database
  lookup. An authenticated learner who obtains another file UUID can extract
  its contents, and `../` identifiers can escape the storage directory.
  Resolve every id through `owned_file`, use the stored extension, reject
  path segments, and make the documents route take a database session.
- [x] **`review_flashcard` and `review_test_item` trust the id.** Both
  record a review against a card/item without checking the owner, so one
  learner can corrupt another's schedule.
- [x] **Test sessions have no owner boundary.** A folder-scoped
  `get_test_items` (`assessment_router.py`) calls `owned_scope`, which only
  parses the folder id, and opens a `TestSession` before proving the folder is
  owned. A caller-supplied `test_session` is not checked against the requested
  test/folder, and `test_session_results` takes no `AuthenticatedUserId` at
  all, so any known session UUID can be closed. Store or derive the owner,
  bind each session to exactly one owned origin, and enforce that invariant
  on open, resume, answer and result routes.
- [x] **The chatbot has no identity at all.** `features/chatbot/chatbot.py`
  takes no `AuthenticatedUserId`; it is protected only by the gateway's JWT
  check, so any authenticated user can spend OpenAI budget without limit and
  no usage can be attributed. Add the dependency, then §LLM cost below.
- [ ] **The refresh cookie has no `Secure` flag.**
  `_issue_refresh_cookie` in `authentication_router.py` sets `httponly` and
  `samesite=strict` but not `secure`, so the refresh token travels over plain
  HTTP. Set it once the gateway terminates TLS.

## P1 — infrastructure before a public launch

- [ ] **No TLS.** `api-gateway/nginx.conf` listens on port 80 only. Put the
  gateway behind TLS (certificates or a terminating proxy), redirect 80 → 443,
  and add HSTS.
- [ ] **Default credentials everywhere.** `docker-compose.yml` hardcodes
  `postgres/postgres`, RabbitMQ runs on `guest/guest`, and Redis has no
  password. Move all of them to injected secrets and close the default users.
- [ ] **`JWT_SECRET_KEY` and `OPENAI_API_KEY` come from a gitignored `.env`.**
  Fine locally; for production they need a real secret store, startup must
  reject a weak JWT key (PyJWT currently warns that the test key is below its
  32-byte recommendation), and rotation needs a documented overlap procedure
  for access, refresh and in-flight task tokens.
- [~] **No application health checks.** Postgres, Redis and RabbitMQ now
  carry `healthcheck` blocks and every service waits on
  `condition: service_healthy`, so the boot race is gone. The services
  themselves still expose no `/health`, so nothing gates the gateway on
  their readiness or reports them unhealthy once running.
- [x] **`create_database_if_not_exists` runs at import time.**
  `content-management-service/src/shared/database.py` connects to Postgres
  while the module is being imported, so an unavailable database is an import
  crash rather than a retryable startup failure.
- [ ] **No backups.** Postgres and the `files` volume have no dump,
  snapshot or restore procedure, and no restore has ever been rehearsed.
- [ ] **The browser origin is hardcoded to localhost in three places.**
  `api-gateway/nginx.conf` and both services' `app_factory.py` accept only
  `http://localhost:3009`; unlike `VITE_GATEWAY_URL`, none is configured from
  the deployment environment. A real web origin will receive no usable CORS
  response. Make one validated origin setting feed the gateway and services,
  and add a production-origin smoke test.
- [ ] **The public responses have no browser security policy.** The frontend
  and gateway nginx configs set no Content-Security-Policy,
  `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` or
  clickjacking defense. Add them at the public edge, with a CSP compatible
  with the SPA/PDF worker, and verify them in a deployed-response test.
- [ ] **Five known dependency advisories are explicitly accepted.**
  `hooks/checks/vulnerable-deps/check` suppresses `PYSEC-2026-161`,
  `PYSEC-2026-248`, `PYSEC-2026-249`, `PYSEC-2026-2280` and
  `PYSEC-2026-2281` because the required Starlette upgrade is blocked by the
  current FastAPI route-wiring tests. Upgrade FastAPI/Starlette, adapt those
  tests and remove every exception before exposing the service.
- [ ] **No rate limiting.** The gateway applies none, so login, sign-up,
  upload, generation and chat are all unthrottled — password guessing and
  cost-burning are free.
  _(claimed 2026-08-29T18:11Z)_
- [ ] **Uploads are barely constrained.** `client_max_body_size 100m` at the
  gateway is the only limit; `file_uploader.py` trusts the client filename's
  extension, and nothing caps per-user storage or scans content.

## P1 — LLM cost control (replaces payments)

- [ ] **Nothing enforces a spend limit.** `provider_keys.monthly_limit_cents`
  and `spent_cents` exist and the settings screen shows them, but no code
  path ever increments `spent_cents` or refuses a generation, so the limit is
  decorative. The default model is `gpt-5-mini`, while `MODEL_RATES` contains
  only `gpt-4.1-nano`, so its computed cost is currently `None` as well.
  Correct the rate table, record cost atomically per call and refuse work past
  the limit.
- [ ] **Sealed provider keys are never used for generation.** A key can be
  saved and opened (`POST /account/provider-keys/{provider}/open`), but the
  generation tasks always use the server's `OPENAI_API_KEY`. Either wire
  bring-your-own-key through generation or stop offering it in the UI.
- [ ] **No global quota for users without a key**, so the shared
  `OPENAI_API_KEY` is an open budget.
- [ ] **Callers choose unbounded LLM work.** `GenerationRequest.ai_model` is
  any string, test/card amounts have no useful upper bound, and generation
  text plus chatbot history have no length or token cap. Allowlist models,
  bound counts and source/history size, estimate the maximum charge before
  queueing, and reject work that cannot fit the user's remaining budget.
- [ ] **Model output is persisted without a schema.** `generated_records`
  accepts any dictionaries, and note fields are converted with `str`, so a
  malformed answer can create empty cards, unusable tests or literal `"None"`
  content while the task reports success. Validate each output type before a
  transaction, reject or quarantine invalid records and return an actionable
  generation failure.
- [ ] **Generation dispatch is neither atomic nor idempotent.** Deck/test
  placeholder rows are committed before `.delay`, and each task is queued one
  at a time; a broker failure or client retry can leave `Generating…` rows,
  partially queued work or duplicate units. Give an import an idempotency key
  and durable state, then make enqueue/retry/cleanup converge on one result.

## P1 — authentication and account lifecycle

- [ ] **The JWT contract is not enforced consistently.** Tokens are issued
  with `iss`, but neither service nor `api-gateway/src/jwt.ts` requires that
  issuer, an audience or even an `exp` claim; the gateway treats a missing
  expiry as valid. Define the claims once and require `iss`, `aud` and `exp`
  at every verifier; access/refresh separation is tracked below.
- [ ] **Refresh tokens cannot be revoked or rotated.** Logout only deletes the
  browser cookie, password changes leave every stolen refresh token valid,
  and `/refresh-token` does not check that its user still exists. Account
  deletion does not clear the cookie, so the deleted browser can mint a ghost
  access token. Store hashed rotating sessions (or a token version), revoke
  them on logout/password change/deletion, detect reuse and check the account
  before refresh.
- [ ] **Credential validation exists mainly in the browser.** Sign-up accepts
  an empty/short password and blank or oversized username at the API, password
  change accepts four characters while the UI promises eight, and username or
  provider-limit overflows reach database constraints as 500s. Put shared
  length/range/normalization rules in Pydantic models and translate uniqueness
  races into stable 4xx responses.
- [ ] **Password recovery is a dead link.** `LoginPage.tsx` labels a link
  “Reset password” but points it back to `/login`; there is no reset-token,
  email-delivery or verified-email flow. Implement expiring single-use reset
  tokens and email verification, or remove the promise before launch.
- [ ] **Changing a password strands every sealed provider key.** Keys are
  derived from the old password in `key_sealing.py`, but `change_password`
  updates only the bcrypt hash. Re-encrypt saved keys during the confirmed
  password change (or require removal first) and test that they remain usable.
- [ ] **Account deletion is not atomic across Postgres and RabbitMQ.**
  `delete_account` publishes `user.deleted` before committing the user delete;
  a later database failure can erase content for an account that still exists,
  while a process failure around the two operations has no reconciliation.
  Use a transactional outbox plus an idempotent consumer and expose deletion
  progress until both stores are reconciled.

## P1 — correctness defects

Carried over from the pre-restructure `to-dos.md` at the repo root and
re-verified against the current source; everything here still reproduces.

- [ ] **Every `created_at` is frozen at import time.** `shared/models/`
  passes `default=datetime.now(UTC)` — a value computed once when the
  module loads, not a callable — in `mixins.py`, `flashcard.py` and
  `assessment.py`. Every row written by one worker process therefore
  carries the same timestamp, which breaks `UnitsApi.sortByNewest` in the
  client and any "recently created" ordering. Confirmed: two notes written
  1.2s apart come back with identical timestamps. Use
  `default=lambda: datetime.now(UTC)`.
- [ ] **`/refresh-token` accepts an access token.** `create_access_token`
  and `create_refresh_token` (`user-service/.../access.py`) put the same
  claims in both tokens and differ only in `exp`, so a stolen access token
  mints fresh ones and the 30-minute lifetime buys nothing. Add a `type`
  claim and verify it in `refresh_token`.
- [ ] **Login answers 404, and says which half was wrong.**
  `login_user` returns 404 `Incorrect email` when the address is unknown
  and 404 `Incorrect password` when it is not. The status should be 401,
  and the two messages should be one — as written they confirm whether an
  address has an account.
- [ ] **Sign-up does not validate the email.** `UserCreate.email` is a bare
  `str` while `UserLogin.email` is `EmailStr` (`schemas.py`), so a garbage
  address registers successfully and can then never log in.
- [ ] **Stored HTML from the model is injected unsanitized.**
  `ui-service/src/features/notes/NotePage.tsx` renders
  `innerHTML={loaded().content}`. Note bodies are model-generated from
  user-supplied source documents, so a poisoned source can plant markup
  that executes when the note is opened. Sanitize before rendering.
- [ ] **Link ingestion will fetch anything.** `extract_link_main_content`
  (`features/study_units_generation/link_extractor.py`) issues
  `requests.get` against a user-supplied URL with a timeout but no
  destination check, so it will happily fetch `169.254.169.254` or any
  service reachable from the container. Block private and link-local
  ranges and refuse redirects into them.
- [ ] **Flashcards due later today are served immediately.** `_due_condition`
  in both `flashcard_router.py` and `flashcard_stats_router.py` applies
  `date(next_review) <= utc_today()` instead of comparing instants. A card due
  in ten minutes stays in the current queue, and a one-card deck can loop it
  immediately. Compare UTC timestamps and test the minute/hour boundary.
- [ ] **Tests are advertised as scheduled, but have no schedule.**
  `TestItem` has no due date or scheduler state; `/test-items` serves every
  item on every attempt, while the landing/result copy says missed questions
  return tomorrow and correct ones later. Implement per-item scheduling and
  due queries/stats, or remove those product claims.
- [ ] **A valid zero-score test result is returned as 404.**
  `test_session_results` checks `if correct`, so a sum of `0` becomes “No
  test stats!” even though it closes the session. Return `{"correct": 0}`
  for a valid session and reserve 404 for an unknown or foreign session.
- [ ] **Review inputs can still crash handlers.** `rating` is an unbounded
  integer and indexes `RATING_MAP`, while `evaluate_accuracy` reads
  `user_answers[0]`; an invalid rating or empty answers reaches `KeyError` or
  `IndexError`. Constrain ratings to 1–4, validate answers by item type and
  return 422 without mutating a review.
- [ ] **API timestamps have no timezone contract.** `date_to_str` emits a
  naive `YYYY-MM-DD HH:MM:SS`, the browser parses it in the device timezone,
  and database columns are timezone-naive even though scheduling is computed
  in UTC. Use timezone-aware storage and ISO 8601 UTC responses so review
  ordering and due calculations agree across regions.
- [ ] **Import failures can leave the UI permanently busy.**
  `ImportDialog.continueToReview` has no `try/finally`, and
  `GenerationStore.start` does not catch upload/extraction/start failures,
  so rejected requests leave “extracting” or progress state behind with no
  retry path. Give every async user journey a recoverable error state and
  prevent duplicate submission while it is pending.

## P1 — public-user obligations

- [ ] **There is no privacy policy, terms of use or AI-processing notice.**
  Users upload documents and URLs that are sent to OpenAI and retained in
  Postgres/files, but the UI states no retention period, subprocessors,
  deletion timing, acceptable-use rules or contact. Publish the applicable
  documents, obtain the required acknowledgement and make actual retention
  and deletion behavior match them.

## P2 — coupling and resilience

- [ ] **FSRS parameters are not per learner.** Scheduling now runs
  in-process (`features/scheduling/flashcard_scheduling.py`) with the
  library defaults for everyone. When the optimizer lands, store each
  learner's tuned parameters in Postgres and load them per review.
- [ ] **`claims_extractor.py` is byte-identical in both services**, so
  the auth contract has two copies that can drift. Either extract a shared
  internal package or accept the duplication deliberately and document it.
- [ ] **No dead-letter queue.** The `user.deleted` consumer
  (`features/user_events/consumer.py`) drops unparseable messages and leaves
  failed ones unacknowledged forever. Add a DLQ and a redelivery limit.
- [ ] **Celery tasks have no retry policy.** A transient OpenAI error fails
  the import with no backoff and no dead-letter.
- [ ] **Browser polling treats one network error as final and has no timeout.**
  `GenerationWatcher.checkOnce` converts the first rejected status request to
  a permanent failed outcome, while a task that remains `PENDING` is polled
  forever. Retry transient HTTP failures with bounded backoff, set a terminal
  deadline and let users reconnect to durable import state after a reload.
- [ ] **`/flashcards` can only ever serve its first page.**
  `get_flashcards` applies `.limit(per_page)` with no `.offset`
  (`flashcard_router.py`), while still reporting `total_flashcards`, so
  every page after the first is unreachable.
- [ ] **Two first loads open two test sessions.** `_ongoing_session`
  (`assessment_router.py`) checks for an ongoing row and then inserts one,
  with no unique constraint on `(origin_id, status)` to make the pair
  atomic, so concurrent opens of the same test each get their own session.
- [ ] **Review writes are not concurrency-safe or idempotent.** Test answers
  query then insert without a unique `(test_session, test_item_id)` constraint,
  and flashcard ratings can be double-submitted while the UI buttons remain
  enabled. Add database uniqueness/locking or idempotency keys so retries and
  double-clicks cannot create duplicate history or advance a card twice.
- [ ] **`TestSession` rows are never cleaned up.** `origin_id`
  (`shared/models/assessment.py`) is a plain column with no foreign key
  and no cascade, and no delete endpoint touches `test_sessions`, so
  sessions and their `TestItemReview` rows outlive the test or folder they
  belong to.
- [ ] **The `files` volume is shared read-write by two services**, which is
  a filesystem-level coupling that will not survive moving either service to
  another host. Object storage would decouple it.

## P2 — observability and operations

- [ ] **No structured logging.** Nothing correlates a request across the
  gateway, the services and the worker; there is no request id.
- [ ] **No metrics and no error tracking.** Nothing reports queue depth,
  generation failure rate, LLM spend or unhandled exceptions.
- [ ] **No resource limits.** LibreOffice and OCR run unbounded in the
  documents deployable; one large document can starve the host.
- [ ] **Single instance of everything.** Postgres, Redis and
  RabbitMQ are all one container with no replication or failover.

## P2 — repository hygiene

- [x] **The legacy root `tests/` scripts are gone.** All tracked Python tests
  now live under the service that owns the code they exercise.
- [x] **The root `to-dos.md` is gone.** It was gitignored and described the
  pre-restructure layout — Kong, `file-processor`, `scheduler-service`,
  MongoDB and the SolidJS-import crashes. Every item still true of the
  current code was carried into this file first; the rest died with the
  architecture it described.
- [ ] **No CI.** Every check runs only in the local pre-commit hook
  (`hooks/checks/`), so nothing enforces them on a pull request.
- [x] **`ui-service` and `api-gateway` carry their own test suites.**
  Vitest with fast-check now stands behind the same two gates the python
  services answer to — `property-tests` and `coverage` (100% branches) — so
  every check but `api-contract` covers TypeScript. `api-contract` stays
  python-only by design: the UI serves no endpoints.
- [x] **Vite emits the favicon correctly.** Although `index.html` references
  `/src/assets/favicon.png`, the production build rewrites it to the hashed
  `/assets/favicon-*.png` file and includes that file in `dist`.
- [ ] **Dependencies are largely unpinned.** `uvicorn`, `PyJWT`,
  `pydantic`, `celery[redis]`, `openai`, `pika`, `python-multipart`,
  `youtube-transcript-api`, `beautifulsoup4` and `fsrs` float in
  `content-management-service/requirements.txt`, as do five in
  `user-service`. A rebuild is not reproducible.
- [ ] **The supported Node toolchain is undefined.** Neither package declares
  `engines` and there is no `.nvmrc`/Volta pin; under the installed Node
  `20.10.0`, UI tests fail before collection on an ESM/CJS incompatibility and
  gateway Vitest fails because `node:util.styleText` is unavailable, even
  though both builds pass. Pin a compatible Node/npm version for developers,
  CI and Docker and prove a clean install runs both suites.
- [ ] **There is no full-stack release test.** The suites replace Postgres,
  Redis, RabbitMQ, Celery, nginx and OpenAI with in-memory fakes or mocks, so
  migrations, proxy routing, cookies/CORS, event cleanup, file sharing and a
  real worker are never exercised together. Add a Compose-based smoke/E2E
  suite for the sign-up, import, generation, review and deletion journey,
  and run it in CI before deployment.
- [ ] **`UserResponse.id` is typed `int`** (`user-service/.../schemas.py`)
  while the `User` primary key is a UUID. Harmless today because nothing
  uses it as a `response_model`, and a serialization error the moment
  something does.
- [ ] **No C3 component diagram.** The content service now holds seven
  features (`file_system`, `file_upload`, `study_units`, `scheduling`,
  `study_units_generation`, `chatbot`, `user_events`) and has outgrown
  the C2 view.

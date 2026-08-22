# Production To-Dos — Leffic

What stands between this repo and a public deployment, in the order it
should be done. Every item names the file that carries the problem, so it
can be checked rather than believed.

**Verdict:** not deployable today. Two frontend defects break the app the
moment it is built for production, and the two review endpoints still
accept an id and act on it without asking who is calling.

Grouped by tier. P0 blocks any exposure at all; P1 blocks a public launch;
P2 is what makes it survivable in the long run.

---

## P0 — the app does not work when built

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
- [ ] **No database migrations anywhere.** Every service calls
  `Base.metadata.create_all` at startup (`shared/database.py`), which
  creates missing tables but never alters existing ones. The `provider_keys`
  table and every future column change will silently not exist on a database
  that already has data. Adopt Alembic per service and run migrations as a
  deploy step.

## P0 — broken access control

Each service decodes the JWT with `verify_signature=False`
(`shared/claims_extractor.py`) and trusts the gateway to have verified it.
That model only holds if no service port is reachable directly — which is
true today, since `docker-compose.yml` publishes only the frontend and the
gateway. Keep it that way. A `user_id` claim that is not a UUID is now
refused with 401 `Token carries an invalid user_id` instead of reaching the
database and failing as a 500. The problem is what happens *after* the
token is trusted: the review endpoints still never check that the caller
owns the row.

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
- [x] **`GET /file` now proves ownership.** `get_file`
  (`features/file_upload/file_uploader.py`) takes `AuthenticatedUserId`
  and resolves the id through `owned_file`
  (`features/file_system/file_access.py`) before it reads anything off
  disk — the same lookup the bookmark endpoints in that feature already
  routed through. A foreign or unknown file id now answers 404 instead
  of streaming the file.
- [ ] **The task-status endpoints have no identity.**
  `/flashcards-status/{task_id}`, `/test-task-status/{task_id}` and
  `/note-task-status/{task_id}` (`task_status_router.py`) take a task id
  and return its result to anyone, so a generated deck, note or test leaks
  to whoever guesses the Celery task id.
- [ ] **`review_flashcard` and `review_test_item` trust the id.** Both
  record a review against a card/item without checking the owner, so one
  learner can corrupt another's schedule.
- [ ] **The chatbot has no identity at all.** `features/chatbot/chatbot.py`
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
  Fine locally; for production they need a real secret store, plus a
  documented rotation procedure for the JWT secret.
- [~] **No application health checks.** Postgres, Redis and RabbitMQ now
  carry `healthcheck` blocks and every service waits on
  `condition: service_healthy`, so the boot race is gone. The services
  themselves still expose no `/health`, so nothing gates the gateway on
  their readiness or reports them unhealthy once running.
- [ ] **`create_database_if_not_exists` runs at import time.**
  `content-management-service/src/shared/database.py` connects to Postgres
  while the module is being imported, so an unavailable database is an import
  crash rather than a retryable startup failure.
- [ ] **No backups.** Postgres and the `files` volume have no dump,
  snapshot or restore procedure, and no restore has ever been rehearsed.
- [ ] **CORS is `allow_origins=["*"]` in every service** (`app_factory.py`).
  Harmless while only the gateway is reachable, dangerous the moment a port
  is exposed. Restrict to the real origin.
- [ ] **No rate limiting.** The gateway applies none, so login, sign-up,
  upload, generation and chat are all unthrottled — password guessing and
  cost-burning are free.
- [ ] **Uploads are barely constrained.** `client_max_body_size 100m` at the
  gateway is the only limit; `file_uploader.py` trusts the client filename's
  extension, and nothing caps per-user storage or scans content.

## P1 — LLM cost control (replaces payments)

- [ ] **Nothing enforces a spend limit.** `provider_keys.monthly_limit_cents`
  and `spent_cents` exist and the settings screen shows them, but no code
  path ever increments `spent_cents` or refuses a generation, so the limit is
  decorative. Record cost per call (the AI client already computes it) and
  refuse work past the limit.
- [ ] **Sealed provider keys are never used for generation.** A key can be
  saved and opened (`POST /account/provider-keys/{provider}/open`), but the
  generation tasks always use the server's `OPENAI_API_KEY`. Either wire
  bring-your-own-key through generation or stop offering it in the UI.
- [ ] **No global quota for users without a key**, so the shared
  `OPENAI_API_KEY` is an open budget.

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
- [ ] **`/flashcards` can only ever serve its first page.**
  `get_flashcards` applies `.limit(per_page)` with no `.offset`
  (`flashcard_router.py`), while still reporting `total_flashcards`, so
  every page after the first is unreachable.
- [ ] **Two first loads open two test sessions.** `_ongoing_session`
  (`assessment_router.py`) checks for an ongoing row and then inserts one,
  with no unique constraint on `(origin_id, status)` to make the pair
  atomic, so concurrent opens of the same test each get their own session.
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

- [ ] **`tests/` at the repo root are legacy scripts.** `login_tests.py` and
  `create_folder_tests.py` import module paths that no longer exist and would
  hit a real database; only `test_extract_link_main_content.py` runs. Delete
  or rewrite them.
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
- [ ] **The favicon points at a source path.** `ui-service/index.html`
  references `/src/assets/favicon.png`, which does not exist in `dist/`, so
  the built site 404s on its own icon.
- [ ] **Dependencies are largely unpinned.** `uvicorn`, `PyJWT`,
  `pydantic`, `celery[redis]`, `openai`, `pika`, `python-multipart`,
  `youtube-transcript-api`, `beautifulsoup4` and `fsrs` float in
  `content-management-service/requirements.txt`, as do five in
  `user-service`. A rebuild is not reproducible.
- [ ] **`ui-service/pnpm-lock.yaml` is tracked but unused** — the
  Dockerfile runs `npm ci`, so the committed pnpm lockfile is a second
  source of truth nothing reads. Delete it.
- [ ] **`UserResponse.id` is typed `int`** (`user-service/.../schemas.py`)
  while the `User` primary key is a UUID. Harmless today because nothing
  uses it as a `response_model`, and a serialization error the moment
  something does.
- [ ] **No C3 component diagram.** The content service now holds seven
  features (`file_system`, `file_upload`, `study_units`, `scheduling`,
  `study_units_generation`, `chatbot`, `user_events`) and has outgrown
  the C2 view.

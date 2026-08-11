# Production To-Dos — Leffic

What stands between this repo and a public deployment, in the order it
should be done. Every item names the file that carries the problem, so it
can be checked rather than believed.

**Verdict:** not deployable today. Two frontend defects break the app the
moment it is built for production, and a whole family of content endpoints
accept an id and act on it without asking who is calling.

Grouped by tier. P0 blocks any exposure at all; P1 blocks a public launch;
P2 is what makes it survivable in the long run.

---

## P0 — the app does not work when built

- [ ] **The production bundle points at `localhost:8888`.**
  `ui-service/Dockerfile` never passes `VITE_GATEWAY_URL`, and Vite inlines
  env vars at build time, so `shared/api/session.ts` falls back to
  `http://localhost:8888` and every API call fails from any other machine.
  Add `ARG VITE_GATEWAY_URL` / `ENV VITE_GATEWAY_URL` to the builder stage
  and pass the real gateway origin at build.
- [ ] **Deep links and refresh return 404.** `ui-service` ships stock
  `nginx:alpine` with no config, so only `/` resolves. `/login`,
  `/folder/home`, `/settings`, `/note/:id` all 404 on reload. Add an nginx
  config with `try_files $uri $uri/ /index.html;` and COPY it in.
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
gateway. Keep it that way. The problem is what happens *after* the token is
trusted: most content endpoints never check that the caller owns the row.

- [ ] **Anyone can delete anyone's content by id.** In
  `features/file_system/content_router.py`, `delete_deck`, `delete_test`,
  `delete_note` and `delete_file` take an id, look it up unscoped and delete
  it — no `AuthenticatedUserId` parameter at all. `delete_folder` in
  `folder_router.py` is the same. Route them through the ownership lookup
  already written for `unit_router.py` (`_owned_content` / `_owned_folder`).
- [ ] **Anyone can read anyone's study material by id.**
  `get_note` (`note_router.py`) filters on `Note.id` alone;
  `get_flashcards?flashcard_deck_id=` (`flashcard_router.py`) filters on the
  deck id alone; `get_test_items?test_id=` (`assessment_router.py`) filters
  on the test id alone. All three leak another learner's content to any
  logged-in caller. Same fix: join to `Folder` and filter on `user_id`.
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
- [ ] **`to-dos.md` at the root is gitignored** and predates the current
  architecture (it still describes Kong and the pre-restructure layout). This
  file replaces it; delete the old one.
- [ ] **No CI.** Every check runs only in the local pre-commit hook
  (`hooks/checks/`), so nothing enforces them on a pull request.
- [ ] **No C3 component diagram.** The content service now holds seven
  features (`file_system`, `file_upload`, `study_units`, `scheduling`,
  `study_units_generation`, `chatbot`, `user_events`) and has outgrown
  the C2 view.

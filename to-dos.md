# Deployment To-Dos — Leffic

Deep analysis of the **Leffic** learning platform (AI-generated flashcards / notes / tests + FSRS spaced repetition).

**Architecture:** SolidJS SPA (nginx) → Kong gateway (JWT + CORS) → 4 FastAPI services
(`user`, `content-management`, `file-processor`, `scheduler`) + Celery worker.
**Stores:** Postgres (`users` + `content` DBs), MongoDB (FSRS scheduler), Redis (Celery broker), shared `files` volume.
**LLM:** OpenAI `gpt-5-mini`, called from `file-processor` (generation) and the chatbot.

> Scope note: payments are **out of scope**. Per-user LLM usage limits **are required** (§4).

**Verdict:** Not deployable yet. There are (a) functional blockers that break core generation, (b) a
**systemic broken-access-control problem** — most data endpoints have no ownership checks and several have no
auth at all — and (c) two hard production breakages in the frontend build/serving. Fix P0 + §2 + §3 before any
public exposure.

---

## P0 — Blockers (broken functionality)

- [ ] **Generation crashes on the active model.** `file-processor/app/tools/ai_manager.py`: `GPT5Mini` never
  sets `input_token_cost` / `output_token_cost` / `cached_token_cost`, but `get_ai_res` always calls
  `get_request_cost()` which reads them → `AttributeError` → caught, retried twice, returns `None` →
  `flashcards, _ = ai.get_ai_res(...)` fails to unpack. Flashcards/notes/tests generation is broken.
  Fix: add current gpt-5-mini pricing fields to `GPT5Mini`, or make `get_request_cost` tolerant.
- [ ] **Runtime dirs may not exist.** `study_units_generator.py` uses `temp_files/` (NamedTemporaryFile
  `dir="temp_files"`) and `files/`. Neither is created in the Dockerfile. Create them at startup or in the
  image, else uploads/temp writes throw.
- [ ] **`OPENAI_API_KEY` is not provided anywhere committed.** `docker-compose.yml` reads `${OPENAI_API_KEY}`
  but `.env` is gitignored. Must be injected from a secret store. (Also: `content-management` has no key set,
  which is fine — it doesn't call OpenAI.)
- [ ] **Likely missing dependency `beautifulsoup4`.** `file-processor/app/tools/link_extractor.py` imports
  `from bs4 import BeautifulSoup`, but `bs4` is in **no** `requirements.txt`. It currently resolves only
  transitively via `textract`; pin `beautifulsoup4` explicitly so link/topic ingestion doesn't break on a
  dependency bump.

## P0 — Frontend build & serving (two guaranteed production breakages)

- [ ] **`VITE_GATEWAY_URL` is never injected at build time.** `ui-service/src/utils/apiRequest.js:2` falls back
  to `http://localhost:8888`. Vite inlines env vars at *build*, and `ui-service/Dockerfile` passes no build
  arg → the production bundle ships pointing at `localhost:8888` and **every API call fails**. Add an
  `ARG VITE_GATEWAY_URL` / `ENV` in the Dockerfile and pass the real gateway URL at build.
- [ ] **No SPA fallback in nginx → deep links & refresh 404.** There is no `nginx.conf`; the image uses stock
  `nginx:alpine` with no `try_files $uri /index.html`. Reloading or deep-linking any route (`/login`,
  `/folder/home`, `/note/:id`, …) returns 404; only `/` works. Add a custom nginx config with an
  `index.html` fallback and COPY it in the Dockerfile.

## 1. Access control — SYSTEMIC (must fix before any exposure)

Root cause: every service decodes the JWT with `verify_signature=False` (trusting Kong), the signing secret
is the hardcoded literal `"my-secret"` (in `user-service/app/tools/access.py` **and** `api-gateway/kong.yml`),
and **all service ports are published to the host** in `docker-compose.yml`. Net effect: an attacker can hit
`8000–8003` directly, bypass Kong, and forge `Authorization: Bearer <hdr>.<{"user_id":"<victim>"}>.` with no
key — becoming any user. Even through Kong, the secret is guessable from the repo.

- [x] **Stop publishing internal ports.** Remove host `ports:` for file-processor (8000), content-management
  (8001), user (8002), scheduler (8003), Postgres (5450), Mongo (27017), Redis (6379). Only the frontend and
  Kong should be reachable. This is the single change that makes the "trust Kong" model valid.
- [ ] **Rotate the JWT secret out of code.** Load from env/secret in both `access.py` and `kong.yml`; rotate.
- [ ] **Add ownership checks — the following endpoints are exploitable IDOR / no-auth today:**
  - **No JWT dependency AND no ownership check (delete by raw ID — destructive):**
    `file_system_manager.py` `DELETE /delete-folder/` (`:74`, recursively deletes subfolders + files from disk),
    `/delete-deck/` (`:279`), `/delete-test/` (`:295`), `/delete-note/` (`:311`),
    `/delete-file/` (`:327`, also unlinks from disk). Any caller can wipe any user's data by ID.
  - **No JWT + writes:** `save-flashcards` (`study_units.py:30`), `save-note` (`:71`), `save-test` (`:95`),
    `save-file-names` (`file_system_manager.py:255`) — inject content into any `folder_id`. These are meant as
    service-to-service calls; they must be moved off the public Kong path and/or protected with an internal
    auth token, not exposed.
  - **Has JWT but ignores it when locating the resource (IDOR by ID enumeration):**
    `GET /flashcards?flashcard_deck_id=` (`study_units.py:148`), `POST /review-flashcard` (`:232`),
    `GET /note` (`:276`), `GET /test-items?test_id=` (`:361`).
  - **No JWT + reads/mutates:** `POST /review-test-item` (`study_units.py:450`),
    `GET /test-session-results` (`:545`, flips session to done).
  - **`GET /api/files/file` (`file_uploader.py:82`) has no auth** — download any user's uploaded file by
    guessing its UUID. High priority.
  - **`POST /schedule-flashcard` (`scheduler flashcard_scheduler.py:28`)** takes `user_id` from the request
    **body**, no JWT — reads/uses any user's FSRS scheduler state. Move internal-only + derive identity from token.
  - Task-status endpoints (`/flashcards-status`, `/note-task-status`, `/test-task-status`) and `POST /chat`
    have no auth (task-result leak by id; LLM-cost abuse on chat).
  - Minor: `create-folder` doesn't verify `parent_folder_id` ownership; `access-folder` notes sub-query
    (`:225`) and `parent_folder_name` (`:140`) aren't user-scoped (info leak).
- [ ] **Pattern fix:** add `get_user_id_from_jwt` to every user-facing endpoint and scope every query/delete by
  `user_id` (join through `Folder.user_id`), the way `/access-folder/` and the `*-stats` endpoints already do.
  Split genuine service-to-service endpoints onto an internal network path Kong doesn't route, guarded by a
  shared internal secret.

## 2. Secrets, transport & CORS

- [ ] **Change default DB credentials** (`postgres/postgres`, hardcoded in compose + each `database.py`); add a
  Mongo password (currently none) and a Redis password.
- [ ] **TLS/HTTPS** at the edge; then set auth cookies `secure=True` (currently `secure=False` in
  `auth.py:57/105/147`, so tokens ride plaintext HTTP) and choose `SameSite` for the deployed domain.
- [ ] **Fix CORS.** Every FastAPI app sets `allow_origins=["*"]` with `allow_credentials=True` (invalid +
  unsafe). Restrict to the real frontend origin; let Kong own CORS per-route and update the hardcoded
  `http://localhost:3009` in `kong.yml` to the production origin.
- [ ] **Stop leaking internals to clients.** Handlers return `str(e)` / `{"error": str(e)}` (e.g. `auth.py:73`,
  many `raise HTTPException(... str(e))`). Return generic messages; log details server-side. Lower Kong's
  `KONG_LOG_LEVEL: debug`.
- [ ] **SSRF on link ingestion.** `extract_link_main_content` (`link_extractor.py:73`) fetches arbitrary
  user-supplied URLs — can reach cloud metadata (169.254.169.254) and internal services. Add an allow-list /
  block private & link-local ranges / disable redirects to internal hosts.
- [ ] **Malware scanning is disabled.** ClamAV service + `scan_file_in_memory` + the upload check are commented
  out (`file_uploader.py`, `docker-compose.yml`). Re-enable before accepting public uploads or document the risk.
- [ ] **Upload limits.** No size / MIME allow-list / count cap on `/upload-files`. Add them (also bounds LLM cost).

## 3. Production infrastructure

- [ ] **DB readiness/healthchecks.** `depends_on` doesn't wait for Postgres/Mongo/Redis to be *ready*; each
  service runs `create_database_if_not_exists()` + `create_all()` at import and will crash on a cold start race.
  Add healthchecks + `condition: service_healthy` (or retry/wait).
- [ ] **`db_port` default mismatch.** `content-management` and `user` `database.py` default `DB_PORT` to `5455`
  while compose/Postgres use `5432`. Works in compose (env overrides) but will bite any non-compose run —
  align the defaults.
- [ ] **Inter-service HTTP has no timeouts.** `requests.post(...)` in `study_units_generator.py` (`:50/90/115`),
  `file_uploader.py` (`:66`), `study_units.py` (`:243`) can hang a worker/request indefinitely. Add timeouts +
  handle failures.
- [ ] **Persistent file storage.** `files` is a local Docker volume shared between containers; move to object
  storage (S3/GCS) for multi-host/scaled deploys.
- [ ] **Schema migrations.** Services use `Base.metadata.create_all` (no Alembic). OK for first deploy; add
  migrations before schema changes ship to a live DB.
- [ ] **Resource limits & worker image.** Set CPU/mem limits; the Celery worker reuses the file-processor image
  (has libreoffice/tesseract/ffmpeg) — verify heavy conversions have enough resources and a concurrency cap.
- [ ] **Observability.** Replace `print`/`traceback` with structured logging; add a health endpoint per service
  and error tracking (e.g. Sentry).
- [ ] **Gateway rate limiting.** Add Kong `rate-limiting` on generation/upload/chat routes as first-line abuse
  defense (complements per-user LLM limits below).

## 4. LLM usage limits (required — replaces payments)

`ai_manager` already computes `get_request_cost` but the result is discarded (`_`), and no per-user usage is
stored. Plan:

- [ ] **Choose the limit model.** Recommend a **monthly quota per user**, either (a) count of generations
  (deck/note/test/chat) — simplest, or (b) token/cost budget — precise. (a) ships fastest.
- [ ] **Usage store.** New table in `user-service` DB keyed by `user_id`, e.g.
  `usage(user_id, period_start, generations_used, tokens_used)`, plus one configurable default limit
  (no paid tiers needed).
- [ ] **Quota endpoints on user-service:** `GET /usage` (remaining) and internal `POST /usage/consume`
  (increment + allow/deny), reachable from `file-processor` over the internal network.
- [ ] **Enforce before spending.** In `generate_study_units` and `chatbot.chat`, check quota *before*
  dispatching Celery tasks / calling OpenAI; return `429` with a clear message when exhausted.
- [ ] **Record real usage.** Stop discarding the cost/token count from `get_ai_res`; report actual tokens after
  each task completes. (Depends on the P0 `GPT5Mini` cost fix.)
- [ ] **Cap per-request size.** Enforce max input text length and max `amount` (flashcards/test items) so a
  single request can't blow the budget regardless of quota.
- [ ] **Surface in UI.** Show remaining quota + a friendly "limit reached" state (notification components already
  exist under `ui-service/src/components/notifications/`).
- [ ] **Period reset.** Reset/roll the quota per period (cron or compute-on-read).

## 5. Cleanup / polish

- [ ] Remove debug `console.log`s leaking request config incl. the `Authorization` header
  (`apiRequest.js:75`) and scattered logs (`Chatbot.jsx`, `AIImport.jsx`, `Home.jsx`, `FlashcardsMainReview.jsx`,
  `FileReview.jsx`, `NotesReview.jsx`, `TestMainReview.jsx`).
- [ ] Fix dead nav link: `LeftNavBar.jsx:92` points to `/explore`, which has no route in `App.jsx`.
- [ ] Favicon `index.html:7` references source path `/src/assets/favicon.png` (404s in `dist/`).
- [ ] Remove committed `.DS_Store` and stray `.pytest_cache/` dirs; drop the stray `pnpm-lock.yaml` (Dockerfile
  uses `npm ci`); add to `.gitignore`.
- [ ] Fill in `README.md` (currently only headings) — setup, env vars, run/build, architecture.
- [ ] Remove/relocate `test.ipynb` and ad-hoc `tests/` scripts; add a real CI (build, lint, test).
- [ ] Pin remaining unpinned deps (`uvicorn`, `celery`, `openai`, `tiktoken`, `PyJWT`, `fsrs`); remove dead code
  (`GPT41Nano`, pyclamd imports) once decisions above are made.

---

## 6. Additional bugs found in deep review (2026-07-06)

New issues from a full-codebase pass — **not** duplicates of §P0–§5 above. Grouped by severity.
All items below were re-verified against source in an adversarial second pass (2026-07-06): **51/53 CONFIRMED**
at the cited lines; 2 marked _(partial)_ where severity depends on an unverified external (fsrs internals).

### 6.1 Critical — frontend crashes on render (missing SolidJS imports)

Every SolidJS control-flow component (`Show`/`For`/`Switch`) must be imported; used-but-not-imported → `createComponent(undefined)` throws and blanks the view. All verified against source.

- [ ] **`ui-service/src/App.jsx:29`** uses `<Show>` but line 9 imports only `{ Match, Switch }`. App is the root → **entire app throws on first render / blank page.**
- [ ] **`ui-service/src/pages/Home.jsx:312`** uses `<For>` but line 1 imports everything *except* `For` → folder page throws once content loads.
- [ ] **`ui-service/src/components/GeneralDropdown.jsx:22`** uses `<Show>`, not imported (line 1). Rendered in `LeftNavBar` (every page) + `AIImport` → crash.
- [ ] **`ui-service/src/components/TestMainReview.jsx:127`** uses `<Switch>` but line 1 imports `{ createSignal, For, Match, onMount, batch }` (no `Switch`) → opening any test throws.
- [ ] **`ui-service/src/components/AIImport.jsx:200,207`** use `<Show>`, imports only `{ createEffect, createSignal }` → opening a folder crashes.
- [ ] **`ui-service/src/components/FileUploader.jsx:77,85`** use `<Show>`, imports only `{ createSignal }` → rendered by `AIImport` → crash.
- [ ] **`ui-service/src/components/NewFolder.jsx:40`** uses `<Show>`, imports only `{ createSignal }` → crashes on folder page.

### 6.2 High — backend correctness (crashes / broken core behavior)

- [ ] **FSRS scheduler never persists.** `scheduler-service/app/apis/flashcard_scheduler.py:37-43`: `schedule_flashcard_fsrs` computes `new_card`/`review_log` and returns them but never writes back to `schedulers_collection` (no `insert_one`/`update_one`). Every call rebuilds a default `Scheduler()`; **spaced repetition never actually advances server-side.** (Core feature broken.)
- [ ] **bcrypt backend missing → signup/login 500.** `user-service/app/tools/access.py:15` uses `CryptContext(schemes=["bcrypt"])` but `requirements.txt` lists `passlib==1.7.4` with **no `bcrypt`** pinned. First `hash_password`/`verify_password` raises `MissingBackendError` (and passlib 1.7.4 also crashes reading `bcrypt.__about__` against bcrypt≥4.1). Pin `bcrypt<4.1`.
- [ ] **`get_ai_res` returns `None` on double failure → unpack crash.** `file-processor/app/tools/ai_manager.py:37-62` falls through to implicit `None` when both retries fail; callers do `flashcards, _ = ai.get_ai_res(...)` (`study_units_generator.py:38,84,110`) → `TypeError: cannot unpack NoneType` → Celery task FAILURE.
- [ ] **Task-status endpoints 500 when the task FAILED.** `file-processor/app/apis/study_units_generator.py:70-77,132-142,146-156`: `ready()` is true for FAILURE too, but then `task_result.result` is the Exception, so `.get("...")` → `AttributeError`. Frontend can never learn a job failed. Guard on `task_result.successful()` / `state == "FAILURE"`.
- [ ] **All `created_at`/`reviewed_at` timestamps are frozen at worker boot.** `content-management/app/models.py:19,39,49,63,86,99,115,124,138` use `default=datetime.now(timezone.utc)` — the value is computed **once at import**, not per-row. Every row gets the same timestamp → ordering / "recently created" / date analytics all wrong. Use `default=lambda: datetime.now(timezone.utc)`.
- [ ] **Intended 404s swallowed into 500s (multiple services).** A broad `except Exception → raise HTTPException(500, str(e))` catches the inner `HTTPException(404/400)`:
  - `content-management/app/apis/study_units.py`: `flashcards_stats` (404 at :593 caught at :641), `notes_stats` (:659/:699).
  - `file-processor/app/apis/file_uploader.py:44-79`: inner `HTTPException(400)` at :63 becomes 500 at :77 (and earlier-written files are orphaned).
  Re-raise `HTTPException` untouched before the generic handler.
- [ ] **content-management image build likely fails on `textract`.** `content-management/requirements.txt:13` pins `textract==1.6.3` but the Dockerfile lacks the `pip<24.1` + `six` upgrade workarounds the file-processor Dockerfile needed (lines 26/28). `textract`/`celery`/`tiktoken`/`openai` are never imported here — remove them to fix the build.
- [ ] **`FileReview.jsx:15` leaks blob URLs.** `URL.createObjectURL(blob)` with no `URL.revokeObjectURL`/`onCleanup` → every viewed file leaks its PDF bytes for the tab's lifetime.
- [ ] **Optimistic delete never checks the response.** `ui-service/src/pages/Home.jsx:84-121`: `deleteUnit` removes the item (line 116) regardless of `.ok`/`null`; a rejected delete vanishes from UI but survives server-side and reappears on refresh, silently.

### 6.3 Medium — logic / data-integrity / UX

- [ ] **Completed test scored 0 returns 404.** `content-management/app/apis/study_units.py:568-574`: after marking session `done`, `if result.correct:` is falsy for `0`/`None` → returns `404 "No test stats!"` for a legitimately-finished test where the user got everything wrong.
- [ ] **`evaluate_accuracy` wrong/crashes.** `study_units.py:445-448`: `if user_answers[0] == 0` → `IndexError` on empty answers, and it inspects only the first selected id (ignores multi-select), corrupting `test_items_stats`.
- [ ] **`prepare_content` assumes `false_options` present.** `study_units.py:316`: `enumerate(content.get("false_options"))` → `TypeError` (None not iterable) if a test item lacks the key → whole `/test-items` 500s.
- [ ] **`save_flashcards` derefs possibly-None folder.** `study_units.py:37-41`: no None check and no `"home"→user_id` mapping → `AttributeError` (500) for `folder_id="home"` or unknown id.
- [ ] **`save_file_names` builds an unpersisted folder with no `user_id`.** `file_system_manager.py:258-271`: on unknown `folder_id` creates a `Folder(name=...)` without `user_id`/`db.add` → commit fails on NOT NULL, file-name rows lost, uploaded files orphaned.
- [ ] **`create_folder` regex from unescaped user input.** `file_system_manager.py:32`: `Folder.name.op("~")(f"^{folder_name}...")` → Postgres `invalid regular expression` (500) for names like `C++ (draft`; metachars also break dedup auto-numbering.
- [ ] **Missing None checks → 500 instead of 404.** `review_flashcard` (:240 `card.fsrs_card`), `get_note` (:286), and `delete_deck`(:287)/`delete_test`(:303)/`delete_note`(:319)/`delete_file`(:330)/`delete_folder`(:102) all deref/`db.delete()` without checking `first()`.
- [ ] **Unregistered file extension crashes generation.** `file-processor/app/tools/text_extractor.py:17-19` returns `None` for unknown extensions; `study_units_generator.py:202-203` then calls `.extract_text` on `None` → `AttributeError`. Uploading `.md`/`.zip`/etc kills the request.
- [ ] **`youtu.be` links bypass transcript extraction.** `study_units_generator.py:205` guards on `"youtube.com" in ...` though `extract_video_id` supports `youtu.be` → short-form links get scraped as web pages (garbage text).
- [ ] **`get_dict_from_text` strips newlines/tabs from *values*.** `ai_manager.py:25-30` runs `replace("\n","").replace("\t","")` over the whole response → breaks cloze verbatim matching and note HTML/`<pre>` content.
- [ ] **`TestMetadata.amount` is dead.** `study_units_generator.py:172-173` sets `amount=10` but `get_test_system_prompt()` (`tests_prompt.py:1`) takes no args → requested test size silently ignored.
- [ ] **`/refresh-token` accepts access tokens.** `user-service/app/apis/auth.py:123-139`: access & refresh tokens carry identical claims (no `type`), so a stolen access token can mint new ones, defeating short lifetimes. Add a `type` claim and verify it.
- [ ] **Wrong status code for bad password (404, should be 401).** `auth.py:91-94`; combined with the distinct "Incorrect email" 404 it also enables account enumeration.
- [ ] **Sign-up email not validated.** `user-service/app/schemas.py:6`: `UserCreate.email: str` (login uses `EmailStr`) → a garbage email registers but can never log in.
- [ ] **Synchronous `pymongo` inside `async` handlers.** `scheduler-service` (`__init__.py:6`, `flashcard_scheduler.py:33,59`): blocking `find_one` in async routes serializes requests / stalls the loop on a slow Mongo. Use `motor` or offload to a threadpool.
- [ ] **`DoughnutDiagram.jsx:8-39` never updates.** Chart built once in `onMount`, reads `props.data1/data2` non-reactively with no effect → stats stay stale after a review until full page reload.
- [ ] **`Home.jsx:35-36,45-46` call `.json()` before checking `.ok`** (unlike `getTestsStats`) → rejects on non-JSON error bodies instead of yielding `undefined`.
- [ ] **`Login.jsx:27` / `SignUp.jsx:45`** `await res.json()` with no try/catch/null-guard, but `apiRequest` can return `null` / empty body → unhandled rejection; button silently does nothing.
- [ ] **`SignUp.jsx:46-51` error checks compare against bare strings** (`resData == "Email already registered"`); if backend returns `{detail: ...}` the duplicate-email/username error is never shown.
- [ ] **`Chatbot.jsx:38-42` duplicates the user bubble** — the `catch` re-appends `{role:"user",...}` already added at line 20, so any network error double-renders the message.
- [ ] **`LeftNavBar.jsx:136` "Settings" is wired to `logoutUser`** (same as Logout, line 135) → clicking Settings logs the user out.
- [ ] **Stored XSS in `NotesReview.jsx:37`** — `innerHTML={note().content}` injects unsanitized AI/server HTML; a stored `<img onerror>`/`<script>` executes. Sanitize (e.g. DOMPurify).
- [ ] **`TestSession` rows orphaned on delete.** `content-management/app/models.py:109-115`: `origin_id` has no FK/cascade and delete endpoints never touch `test_sessions` → dangling sessions + `TestItemReview` analytics rows accumulate.
- [ ] _(partial)_ **`schedule_flashcard` stored doc keeps `user_id` for `Scheduler.from_dict`.** `scheduler-service/app/apis/flashcard_scheduler.py:33-34,59-60`: `mongo_row2dict` strips only `_id`, so the dict passed to `Scheduler.from_dict` (`tools/flashcard_scheduler.py:21`) still carries `user_id`. Latent today (find_one always returns None until the persistence bug in §6.2 is fixed); whether fsrs's `from_dict` actually raises on the extra key is unconfirmed — fix defensively alongside persistence.

### 6.4 Low — polish / robustness

- [ ] **`upload_files` orphans files with no cleanup.** `file-processor/app/apis/file_uploader.py`: files written per-iteration to `files/` with no rollback on later failure and nothing ever deletes them → unbounded growth.
- [ ] **`generate_study_units` returns HTTP 200 on internal error.** `study_units_generator.py:250-252`: broad `except` returns `{"err": str(e)}` with default 200 → callers treating 2xx as success proceed with no task IDs. Also `flashcards.pop("deck_name")` (:47) `KeyError`s if the model omits the key.
- [ ] **Duplicate function names shadow earlier defs** — `save_note` (`study_units.py:72` & `:96`), `delete_test` (`file_system_manager.py:296` & `:312`). Routing works via decorators but direct import/testing hits the shadow.
- [ ] **`/flashcards` has no offset.** `study_units.py:160-172,206-218` apply `.limit(per_page)` with no `.offset` → only the first page of due cards is ever reachable despite `total_flashcards`.
- [ ] **`get_test_items` can create duplicate ongoing sessions** under concurrent first-loads (`study_units.py:339-356`, check-then-insert, no unique constraint on `(origin_id, status)`).
- [ ] **`TestMainReview.jsx:181-188` Back/Next not disabled during async** review/page fetch → rapid clicks overlap and can corrupt `itemIndex`/`page` + persisted `localStorage` cursor.
- [ ] **`apiRequest.js:26-33` `getAccessToken` returns `undefined` on non-401 refresh errors** (e.g. 500) with no logging → a transient refresh outage is indistinguishable from real auth failure.
- [ ] **`claims_extractor` (scheduler) allows `user_id=None` filter.** `scheduler-service/app/tools/claims_extractor.py:15`: `payload.get("user_id")` → Mongo filter `{"user_id": None}` instead of rejecting a token missing the claim.
- [ ] **`UserResponse.id: int` vs UUID PK.** `user-service/app/schemas.py:11` contradicts `models.py:10` (UUID); would fail serialization if ever used as a `response_model`. Also `schedule_flashcard_fsrs` has dead `timestamp = datetime.now(...)` (`flashcard_scheduler.py:13`).
- [ ] _(partial)_ **`scheduler-service` pulls `fsrs[optimizer]`** (torch/pandas) onto `python:3.12-slim` (`requirements.txt:1`, base image `Dockerfile:1`) with no compiler installed → **image bloat is certain**; the build-failure risk is speculative (torch normally ships cp312 wheels) and would only bite if a transitive dep fell back to an sdist. Use plain `fsrs` unless the optimizer is actually run.
- [ ] **`create_database_if_not_exists` f-string SQL identifier.** `user-service/app/database.py:30,35` interpolates `db_name` — safe today (literal `"users"`) but breaks/injects if ever made configurable.

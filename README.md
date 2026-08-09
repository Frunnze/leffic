# Leffic

Turn any file, link or topic into flashcards, a note and a test — then
review them exactly when you are about to forget.

Thesis link: link

## Demo

[Video](https://drive.google.com/file/d/1QQh3qZqyipiuo7TKyoSCjWW-QDhHSaZe/view?usp=sharing)

## What it does

You drop material into a folder — an uploaded document, a URL, a YouTube
link, or just a topic you type. One import fans out into three generations
at once: a flashcard deck, a written note and a multiple-choice test, each
arriving as it finishes.

From there the folder is a study surface. It shows what is due today across
itself and every subfolder beneath it, so a whole subject can be reviewed in
one pass. Flashcards are scheduled with FSRS and each answer button carries
the interval it would buy you. Tests are paginated and resumable — leave one
half-finished and it picks up where you left off. Notes mark themselves read
when opened.

| Area | What you can do |
|---|---|
| Folders | Nest them freely; `home` resolves to your own root folder |
| Import | From a file, a web page, a YouTube transcript, or a bare topic |
| Flashcards | Review with Again / Hard / Good / Easy, each labelled with its next interval |
| Tests | Multiple choice, paginated, resumable, with a result screen |
| Notes | Generated HTML, marked read on open, with a reading-time estimate |
| Files | Any uploaded format is converted to PDF for viewing |
| Mixed review | Sweep every due card or test item across a folder and its whole subtree |
| Ask | A general-purpose chatbot panel |

## Requirements

- Docker and Docker Compose
- An `OPENAI_API_KEY`

## Running it

```bash
docker compose up --build
```

The web app is served on <http://localhost:3009> and every API call goes
through the gateway on <http://localhost:8888>. No other service publishes a
port — they are reachable only from inside the compose network.

The environment needs `OPENAI_API_KEY`, `JWT_SECRET_KEY`, and the Postgres
credentials consumed by `docker-compose.yml`.

## Architecture

Six deployables and four datastores. Every backend service is FastAPI on
Python 3.12 with the same layout — `run.py` → `app_factory.py` →
`features/` and `shared/`.

<p align="center">
  <img src="docs/diagrams/c1/c1-system-context.png" alt="System context (C1)" width="620">
  <br>
  <em>Who uses Leffic and what it talks to.</em>
</p>

<p align="center">
  <img src="docs/diagrams/c2/c2-containers.png" alt="Containers (C2)" width="760">
  <br>
  <em>The pieces inside it and how they communicate.</em>
</p>

| Service | Holds | Talks to |
|---|---|---|
| `ui-service` | SolidJS SPA, built by Vite, served by nginx | the gateway |
| `api-gateway` | Kong, DB-less; verifies the JWT and applies CORS | every service |
| `user-service` | Accounts and the only JWT issuer | Postgres `users` |
| `content-management-service` | Folders, decks, cards, tests, notes, file rows, review history | Postgres `content`, scheduler |
| `file-processor-service` | Uploads, text extraction, PDF conversion, chatbot | Redis, OpenAI, content service |
| `celery-worker` | The three generation tasks, same image as the file processor | OpenAI, content service |
| `scheduler-service` | FSRS next-review dates and interval labels | MongoDB |

### How a request is authorised

`user-service` issues an HS256 access token (30 min) and sets a refresh
token as an httpOnly cookie (7 days). The browser keeps the access token in
memory only, and the HTTP client refreshes and retries once on a 401.

Kong is the only place a signature is verified. Behind it every service
decodes the token without verification and trusts the `user_id` claim, so a
service reached without passing through the gateway would accept a forged
identity.

### How an import flows

The file processor extracts the text in the request itself, then enqueues one
Celery task per study-unit type. The browser polls each task id until it
succeeds. Each finished task posts its result to the content service, which
is the system of record.

## Data

| Store | Engine | Holds |
|---|---|---|
| `users` | PostgreSQL | accounts, password hashes |
| `content` | PostgreSQL | folders, decks, flashcards, tests, test items, sessions, notes, files, reviews |
| `fsrs_db` | MongoDB | per-user FSRS scheduler parameters |
| `files` | Docker volume | the uploaded documents themselves |
| Redis | — | Celery broker and result backend |

Schemas are created on startup with `Base.metadata.create_all` — there are no
migrations. A user's root folder is the folder whose id equals their user id.

## Quality gate

`hooks/pre-commit` runs every check in `hooks/checks/` across all four Python
services, and a commit fails if any of them does:

| Check | Enforces |
|---|---|
| file length | no file over 200 lines |
| definition names | one responsibility per name |
| nested definitions | no `def` inside a `def` |
| class methods | one job per class |
| duplicate code | pylint `R0801`, per service |
| dead code | vulture, per service |
| ruff | every rule, at 79 columns |
| basedpyright | `typeCheckingMode = "all"` |
| coverage | 100% branch coverage, per service |
| mutation | mutmut over each service, no surviving mutants |

Install it with `git config core.hooksPath hooks`.

## Tech stack

- SolidJS, TypeScript, Vite
- FastAPI, SQLAlchemy, Pydantic
- Kong
- Celery, Redis
- PostgreSQL, MongoDB
- OpenAI
- py-fsrs
- Docker Compose

## Functional and non-functional requirements

## Tasks

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.  
See the [LICENSE](./LICENSE) file for details.

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

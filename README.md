# Leffic

Turn any file, link or topic into flashcards, a note and a test, then
review them exactly when you are about to forget.

## Demo

[Video](https://drive.google.com/file/d/1QQh3qZqyipiuo7TKyoSCjWW-QDhHSaZe/view?usp=sharing)

## What it does

Drop material into a folder and one import fans out into three generations
at once: a flashcard deck, a written note and a multiple-choice test. The
folder then shows what is due today across itself and every subfolder
beneath it.

| Area | What you can do |
|---|---|
| Folders | Nest them freely; `home` resolves to your own root folder |
| Import | From a file, a web page, a YouTube transcript, or a bare topic |
| Flashcards | Again / Hard / Good / Easy, each labelled with its next interval |
| Tests | Multiple choice, paginated, resumable, with a result screen |
| Notes | Generated HTML, marked read on open, with a reading-time estimate |
| Files | Any uploaded format is converted to PDF for viewing |
| Mixed review | Every due card or test item across a folder and its subtree |
| Ask | A general-purpose chatbot panel |

## Requirements

- Docker and Docker Compose
- An `OPENAI_API_KEY`

## Running it

```bash
docker compose up --build
```

The web app is on <http://localhost:3009>, the gateway on
<http://localhost:8888>. Nothing else publishes a port.

Set `OPENAI_API_KEY`, `JWT_SECRET_KEY` and the Postgres credentials from
`docker-compose.yml`.

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
| `content-management-service` | Folders, decks, cards, tests, notes, file rows, reviews | Postgres `content`, scheduler |
| `file-processor-service` | Uploads, text extraction, PDF conversion, chatbot | Redis, OpenAI, content service |
| `celery-worker` | The three generation tasks, same image as the file processor | OpenAI, content service |
| `scheduler-service` | FSRS next-review dates and interval labels | MongoDB |

### How an import flows

The file processor extracts the text, then enqueues one Celery task per
study-unit type. The browser polls each task id until it succeeds, and each
finished task posts its result to the content service.

## Data

| Store | Engine | Holds |
|---|---|---|
| `users` | PostgreSQL | accounts, password hashes |
| `content` | PostgreSQL | folders, decks, flashcards, tests, sessions, notes, files, reviews |
| `fsrs_db` | MongoDB | per-user FSRS scheduler parameters |
| `files` | Docker volume | the uploaded documents themselves |
| Redis | — | Celery broker and result backend |

Schemas are created on startup with `Base.metadata.create_all` — there are no
migrations. A user's root folder is the folder whose id equals their user id.

## Tech stack

- SolidJS, TypeScript, Vite
- FastAPI, SQLAlchemy, Pydantic
- Kong
- Celery, Redis
- PostgreSQL, MongoDB
- OpenAI
- py-fsrs
- Docker Compose

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.  
See the [LICENSE](./LICENSE) file for details.

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

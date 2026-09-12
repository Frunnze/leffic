"""Classify known, explicitly resolved library operations by I/O concern."""

# Only resolved library calls count; arbitrary names such as db.save do not.
# Constructors, logging, serialization and path manipulation are not effects.
EFFECT_RULES = (
    (
        "filesystem",
        (
            "pathlib",
            "os",
            "shutil",
            "aiofiles",
            "node:fs",
            "fs",
            "fs/promises",
            "node:fs/promises",
            "builtins.open",
        ),
        {
            "open",
            "read",
            "write",
            "read_text",
            "write_text",
            "read_bytes",
            "write_bytes",
            "unlink",
            "remove",
            "mkdir",
            "rmdir",
            "listdir",
            "rename",
            "copy",
            "copyfile",
            "rmtree",
            "readFile",
            "writeFile",
            "readFileSync",
            "writeFileSync",
            "readdir",
            "readdirSync",
            "stat",
        },
    ),
    (
        "network",
        (
            "requests",
            "httpx",
            "aiohttp",
            "urllib.request",
            "axios",
            "node:http",
            "node:https",
            "global.fetch",
        ),
        {
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "request",
            "send",
            "urlopen",
            "urlretrieve",
            "fetch",
            "head",
        },
    ),
    (
        "persistence",
        (
            "sqlalchemy",
            "sqlite3",
            "psycopg",
            "psycopg2",
            "asyncpg",
            "pg",
            "mysql2",
            "@prisma/client",
            "global.localStorage",
            "global.sessionStorage",
        ),
        {
            "execute",
            "executemany",
            "query",
            "commit",
            "flush",
            "add",
            "delete",
            "fetch",
            "fetchrow",
            "fetchall",
            "fetchone",
            "rollback",
            "findMany",
            "findUnique",
            "create",
            "update",
            "setItem",
            "getItem",
            "removeItem",
        },
    ),
    (
        "process",
        ("subprocess", "child_process", "node:child_process"),
        {
            "run",
            "Popen",
            "call",
            "check_call",
            "check_output",
            "exec",
            "execSync",
            "execFile",
            "spawn",
            "spawnSync",
        },
    ),
    (
        "presentation",
        ("jinja2", "django.template", "react-dom", "global.document"),
        {
            "render",
            "render_to_string",
            "createElement",
            "querySelector",
            "getElementById",
            "write",
        },
    ),
)


def effect_domains(calls: list[str]) -> dict[str, list[str]]:
    domains: dict[str, set[str]] = {}
    for call in calls:
        for domain, prefixes, operations in EFFECT_RULES:
            if call.rsplit(".", 1)[-1] not in operations:
                continue
            if any(call == p or call.startswith(p + ".") for p in prefixes):
                domains.setdefault(domain, set()).add(call)
    return {name: sorted(calls) for name, calls in sorted(domains.items())}

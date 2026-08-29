from pathlib import Path

from alembic.config import Config

_ALEMBIC_INI_NAME = "alembic.ini"
_MISSING_ALEMBIC_INI = "No alembic.ini above this test file"

INITIAL_REVISION = "c750ff70652b"


def service_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / _ALEMBIC_INI_NAME).is_file():
            return candidate

    raise RuntimeError(_MISSING_ALEMBIC_INI)


def alembic_config(database_url: str) -> Config:
    root = service_root()
    config = Config(str(root / _ALEMBIC_INI_NAME))
    config.set_main_option("script_location", str(root / "migrations"))
    config.set_main_option("sqlalchemy.url", database_url)

    return config

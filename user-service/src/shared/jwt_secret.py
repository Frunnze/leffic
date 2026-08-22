import os

_configured_key = os.getenv("JWT_SECRET_KEY")

if not _configured_key:
    _UNSET_ENVIRONMENT = "JWT_SECRET_KEY environment variable is not set"
    raise RuntimeError(_UNSET_ENVIRONMENT)

SECRET_KEY: str = _configured_key
ALGORITHM = "HS256"

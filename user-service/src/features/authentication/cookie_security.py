import os

_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_FALSE_VALUES = frozenset({"0", "false", "no", "off"})

_configured_value = (
    os.getenv("REFRESH_COOKIE_SECURE", "true").strip().lower()
)

if _configured_value not in _TRUE_VALUES | _FALSE_VALUES:
    _UNREADABLE_SETTING = (
        "REFRESH_COOKIE_SECURE must be one of "
        "1, true, yes, on, 0, false, no, off"
    )
    raise RuntimeError(_UNREADABLE_SETTING)

REFRESH_COOKIE_SECURE: bool = _configured_value in _TRUE_VALUES

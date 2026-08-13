from datetime import UTC, date, datetime, timedelta, tzinfo

import pytest

from shared import clock


class FixedDatetime:
    @staticmethod
    def now(tz: tzinfo | None = None) -> datetime:
        dateobj = datetime(2026, 8, 8, 1, 30, tzinfo=UTC)

        if tz is None:
            return (dateobj - timedelta(hours=3)).replace(tzinfo=None)

        return dateobj


def test_today_is_read_in_utc(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(clock, "datetime", FixedDatetime)

    assert clock.utc_today() == date(2026, 8, 8)

import uuid
from typing import final, override

from sqlalchemy import Dialect, Uuid
from sqlalchemy.types import TypeDecorator


@final
class FlexibleUuid(TypeDecorator[uuid.UUID]):
    impl = Uuid(as_uuid=True)
    cache_ok = True

    @override
    def process_bind_param(
        self, value: object, dialect: Dialect
    ) -> uuid.UUID | None:
        if value is None:
            return None

        if isinstance(value, uuid.UUID):
            return value

        return uuid.UUID(str(value))

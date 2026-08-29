from typing import Self


class FakeCursor:
    def __init__(self, existing: tuple[int] | None) -> None:
        super().__init__()
        self.existing: tuple[int] | None = existing
        self.statements: list[object] = []
        self.parameters: list[object] = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def execute(self, statement: object, *arguments: object) -> None:
        self.statements.append(statement)
        self.parameters.extend(arguments)

    def fetchone(self) -> tuple[int] | None:
        return self.existing


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        super().__init__()
        self.cursor_object: FakeCursor = cursor
        self.entered: bool = False
        self.closed: bool = False
        self.statements_before_autocommit: int | None = None
        self._autocommit: bool = False

    def __enter__(self) -> Self:
        self.entered = True
        return self

    def __exit__(self, *_: object) -> None:
        return None

    @property
    def autocommit(self) -> bool:
        return self._autocommit

    @autocommit.setter
    def autocommit(self, enabled: bool) -> None:
        self._autocommit = enabled
        self.statements_before_autocommit = len(self.cursor_object.statements)

    def cursor(self) -> FakeCursor:
        return self.cursor_object

    def close(self) -> None:
        self.closed = True

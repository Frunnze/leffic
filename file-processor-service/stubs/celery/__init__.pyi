from collections.abc import Callable

class TaskResult:
    @property
    def id(self) -> str: ...

class RegisteredTask:
    def delay(self, **kwargs: object) -> TaskResult: ...

class Celery:
    def __init__(
        self,
        main: str | None = ...,
        *,
        broker: str | None = ...,
        backend: str | None = ...,
        include: list[str] | None = ...,
    ) -> None: ...
    def task(self, fun: Callable[..., object], /) -> RegisteredTask: ...

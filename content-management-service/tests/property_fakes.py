from types import TracebackType
from typing import Protocol, final

from httpx import Request
from openai import APIConnectionError


class AnsweringAi(Protocol):
    def get_ai_res_hist(
        self, system_prompt: str, history: list[object]
    ) -> str: ...


@final
class FakeAiManager:
    def __init__(self, payload: dict[str, object], answer: str = "") -> None:
        self.payload: dict[str, object] = payload
        self.answer: str = answer
        self.system_prompts: list[str] = []

    def get_ai_res(
        self, system_prompt: str, user_prompt: str
    ) -> tuple[dict[str, object], float | None]:
        _ = user_prompt
        self.system_prompts.append(system_prompt)

        return self.payload, None

    def get_ai_res_hist(
        self, system_prompt: str, history: list[object]
    ) -> str:
        _ = system_prompt
        _ = history

        return self.answer


@final
class UnavailableAiManager:
    def get_ai_res_hist(
        self, system_prompt: str, history: list[object]
    ) -> str:
        _ = system_prompt
        _ = history

        raise APIConnectionError(request=Request("POST", "https://ai"))


@final
class FakeAiFactory:
    def __init__(self, manager: AnsweringAi) -> None:
        self.manager: AnsweringAi = manager

    def get_ai(self, model: str | None = None) -> AnsweringAi:
        _ = model

        return self.manager


@final
class FakeQueuedTask:
    def __init__(self, task_id: str) -> None:
        self.task_id: str = task_id

    def delay(self, **arguments: object) -> "FakeQueuedTask":
        _ = arguments

        return self

    @property
    def id(self) -> str:
        return self.task_id


@final
class FakeTaskResult:
    def __init__(
        self, status: str, result: object, *, finished: bool
    ) -> None:
        self.status: str = status
        self.result: object = result
        self.finished: bool = finished

    def ready(self) -> bool:
        return self.finished


@final
class FakeAsyncResult:
    def __init__(
        self, status: str, result: object, *, finished: bool
    ) -> None:
        self.task_result: FakeTaskResult = FakeTaskResult(
            status, result, finished=finished
        )

    def __call__(
        self, *arguments: object, **keywords: object
    ) -> FakeTaskResult:
        _ = arguments
        _ = keywords

        return self.task_result


@final
class RecordingSave:
    def __init__(self, saved_id: str) -> None:
        self.saved_id: str = saved_id
        self.arguments: tuple[object, ...] = ()

    def __call__(self, *arguments: object) -> str:
        self.arguments = arguments

        return self.saved_id


@final
class RecordingAppend:
    def __init__(self, written: int) -> None:
        self.written: int = written
        self.arguments: tuple[object, ...] = ()

    def __call__(self, *arguments: object) -> int:
        self.arguments = arguments

        return self.written


@final
class FakeTemporaryStorage:
    def __init__(self, directory: str) -> None:
        self.directory: str = directory

    def __enter__(self) -> str:
        return self.directory

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


@final
class RecordingQueuedTask:
    def __init__(self, task_id: str) -> None:
        self.task_id: str = task_id
        self.calls: list[dict[str, object]] = []

    def delay(self, **arguments: object) -> "RecordingQueuedTask":
        self.calls.append(arguments)

        return self

    @property
    def id(self) -> str:
        return self.task_id

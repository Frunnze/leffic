from types import TracebackType
from typing import final


@final
class FakeAiManager:
    def __init__(self, payload: dict[str, object], answer: str = "") -> None:
        self.payload: dict[str, object] = payload
        self.answer: str = answer

    def get_ai_res(
        self, system_prompt: str, user_prompt: str
    ) -> tuple[dict[str, object], float | None]:
        _ = system_prompt
        _ = user_prompt

        return self.payload, None

    def get_ai_res_hist(
        self, system_prompt: str, history: list[object]
    ) -> str:
        _ = system_prompt
        _ = history

        return self.answer


@final
class FakeAiFactory:
    def __init__(self, manager: FakeAiManager) -> None:
        self.manager: FakeAiManager = manager

    def get_ai(self, model: str | None = None) -> FakeAiManager:
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
class FakeAmqpChannel:
    def __init__(self) -> None:
        self.declared_exchange: str = ""
        self.bound: dict[str, str] = {}

    def exchange_declare(
        self, *, exchange: str, exchange_type: str, durable: bool
    ) -> None:
        _ = exchange_type
        _ = durable
        self.declared_exchange = exchange

    def queue_declare(self, *, queue: str, durable: bool) -> None:
        _ = queue
        _ = durable

    def queue_bind(
        self, *, queue: str, exchange: str, routing_key: str
    ) -> None:
        self.bound = {
            "queue": queue,
            "exchange": exchange,
            "routing_key": routing_key,
        }

    def basic_consume(
        self, *, queue: str, on_message_callback: object
    ) -> None:
        _ = queue
        _ = on_message_callback

    def start_consuming(self) -> None:
        return None


@final
class FakeAmqpConnection:
    def __init__(self) -> None:
        self.opened_channel: FakeAmqpChannel = FakeAmqpChannel()

    def channel(self) -> FakeAmqpChannel:
        return self.opened_channel

    def close(self) -> None:
        return None


@final
class RecordingSave:
    def __init__(self, saved_id: str) -> None:
        self.saved_id: str = saved_id
        self.arguments: tuple[object, ...] = ()

    def __call__(self, *arguments: object) -> str:
        self.arguments = arguments

        return self.saved_id


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

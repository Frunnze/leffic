from typing import final


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

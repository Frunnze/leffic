from abc import ABC, abstractmethod


class TaskTokenSigner(ABC):
    @abstractmethod
    def signed_task_id(self, task_id: str, folder_id: str) -> str: ...


class TaskTokenVerifier(ABC):
    @abstractmethod
    def verified_task_id(self, token: str) -> tuple[str, str]: ...

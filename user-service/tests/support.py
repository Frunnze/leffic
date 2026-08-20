from collections.abc import Iterator
from typing import cast, final

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker


@final
class SessionProvider:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        super().__init__()
        self.session_factory: sessionmaker[Session] = session_factory

    def __call__(self) -> Iterator[Session]:
        session = self.session_factory()
        try:
            yield session
        finally:
            session.close()


@final
class Accounts:
    email = "learner@example.com"
    username = "learner"
    phrase = "correct horse battery staple"
    new_phrase = "a much longer phrase to remember"
    other_phrase = "a different phrase entirely"
    wrong_phrase = "not the phrase"
    openai_key = "sk-live-000000000000000007Xa2"
    gemini_key = "gm-live-22222222222222225Kc9"

    def __init__(self, client: TestClient) -> None:
        super().__init__()
        self.client: TestClient = client

    def sign_up(
        self,
        username: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> dict[str, str]:
        response = self.client.post(
            "/sign-up",
            json={
                "username": username or Accounts.username,
                "email": email or Accounts.email,
                "password": password or Accounts.phrase,
            },
        )
        body = cast("dict[str, str]", response.json())

        return {"Authorization": f"Bearer {body['access_token']}"}

    def save_key(
        self,
        headers: dict[str, str],
        provider: str = "openai",
        key: str | None = None,
        password: str | None = None,
    ) -> None:
        _ = self.client.put(
            "/account/provider-keys",
            json={
                "provider": provider,
                "key": key or Accounts.openai_key,
                "password": password or Accounts.phrase,
            },
            headers=headers,
        )

    def open_key(
        self,
        headers: dict[str, str],
        provider: str = "openai",
        password: str | None = None,
    ) -> dict[str, object]:
        response = self.client.post(
            f"/account/provider-keys/{provider}/open",
            json={"password": password or Accounts.phrase},
            headers=headers,
        )

        return {
            "status": response.status_code,
            "body": cast("dict[str, str]", response.json()),
        }

    def keys(self, headers: dict[str, str]) -> list[dict[str, object]]:
        body = cast(
            "dict[str, object]",
            self.client.get(
                "/account/provider-keys", headers=headers
            ).json(),
        )

        return cast("list[dict[str, object]]", body["provider_keys"])

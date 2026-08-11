from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app_factory import create_app

_ORIGIN = "http://localhost:3009"


def _preflight() -> dict[str, str]:
    with TestClient(create_app()) as client:
        response = client.options(
            "/save-note",
            headers={
                "Origin": _ORIGIN,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "X-Custom",
            },
        )

    return dict(response.headers)


def test_any_origin_is_allowed() -> None:
    assert _preflight()["access-control-allow-origin"] == _ORIGIN


def test_credentials_are_allowed() -> None:
    assert _preflight()["access-control-allow-credentials"] == "true"


def test_the_requested_method_is_allowed() -> None:
    assert "POST" in _preflight()["access-control-allow-methods"]


def test_the_requested_headers_are_allowed() -> None:
    assert "X-Custom" in _preflight()["access-control-allow-headers"]


def test_every_router_is_registered() -> None:
    app = create_app()
    paths = {
        route.path for route in app.routes if isinstance(route, APIRoute)
    }

    assert {
        "/chat",
        "/flashcards",
        "/flashcards-stats",
        "/test-items",
        "/test-items-stats",
        "/note",
        "/notes-stats",
        "/create-folder",
        "/upload-files",
        "/file",
        "/extract-text",
        "/generate-study-units",
    } <= paths

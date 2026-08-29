import pytest
from fastapi.routing import APIRoute

from app_factory import create_app
from shared.claims_extractor import get_user_id_from_jwt
from shared.database import get_db

_SESSION_SCOPED_ROUTES = (
    ("/delete-deck/", "DELETE"),
    ("/delete-test/", "DELETE"),
    ("/delete-note/", "DELETE"),
    ("/delete-file/", "DELETE"),
    ("/delete-folder/", "DELETE"),
    ("/note", "GET"),
    ("/flashcards", "GET"),
    ("/test-items", "GET"),
    ("/flashcards-status/{task_id}", "GET"),
    ("/test-task-status/{task_id}", "GET"),
    ("/note-task-status/{task_id}", "GET"),
    ("/upload-files", "POST"),
    ("/extract-text", "POST"),
)

_CALLER_SCOPED_ROUTES = (*_SESSION_SCOPED_ROUTES, ("/chat", "POST"))


class _UnregisteredRouteError(AssertionError):
    def __init__(self, method: str, path: str) -> None:
        super().__init__(f"{method} {path} is not registered")


def _dependencies_of(path: str, method: str) -> set[object]:
    matching = [
        route
        for route in create_app().routes
        if isinstance(route, APIRoute)
        and route.path == path
        and method in route.methods
    ]

    if not matching:
        raise _UnregisteredRouteError(method, path)

    return {
        dependency.call
        for dependency in matching[0].dependant.dependencies
    }


@pytest.mark.parametrize(("path", "method"), _CALLER_SCOPED_ROUTES)
def test_a_scoped_endpoint_identifies_its_caller(
    path: str, method: str
) -> None:
    assert get_user_id_from_jwt in _dependencies_of(path, method)


@pytest.mark.parametrize(("path", "method"), _SESSION_SCOPED_ROUTES)
def test_a_scoped_endpoint_keeps_its_database_session(
    path: str, method: str
) -> None:
    assert get_db in _dependencies_of(path, method)


def test_chat_depends_on_identity_and_nothing_else() -> None:
    assert _dependencies_of("/chat", "POST") == {get_user_id_from_jwt}

import subprocess
import sys
from pathlib import Path

from typescript_finder_support import CHECKS

_FINDER = CHECKS / "open-closed" / "variant_dispatches.py"


def report_from(tmp_path: Path, files: dict[str, str]) -> list[str]:
    paths: list[str] = []

    for relative, source in files.items():
        module = tmp_path / relative
        module.parent.mkdir(parents=True, exist_ok=True)
        _ = module.write_text(source, encoding="utf-8")
        paths.append(relative)

    finished = subprocess.run(
        [sys.executable, str(_FINDER)],
        input="\n".join(paths),
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )

    return finished.stdout.splitlines()


def test_flags_behavior_split_across_python_registries(
    tmp_path: Path,
) -> None:
    files = {
        "src/policy.py": (
            "from typing import Literal\n"
            "Channel = Literal['email', 'sms', 'push']\n"
            "ENDPOINTS: dict[Channel, str] = {\n"
            "    'email': '/email', 'sms': '/sms', 'push': '/push'\n"
            "}\n"
            "LABELS: dict[Channel, str] = {\n"
            "    'email': 'Email', 'sms': 'SMS', 'push': 'Push'\n"
            "}\n"
        )
    }

    assert report_from(tmp_path, files) == [
        (
            "src/policy.py:3: Channel behavior is split across 2 "
            "registries in 1 file: ENDPOINTS, LABELS"
        )
    ]


def test_does_not_merge_unrelated_python_registry_domains(
    tmp_path: Path,
) -> None:
    files = {
        "src/policy.py": (
            "FIRST = {'email': 1, 'sms': 2, 'push': 3}\n"
            "SECOND = {'small': 1, 'medium': 2, 'large': 3}\n"
        )
    }

    assert report_from(tmp_path, files) == []


def test_flags_typed_python_branch_outside_behavior_registry(
    tmp_path: Path,
) -> None:
    files = {
        "src/models.py": (
            "from typing import Literal\n"
            "Channel = Literal['email', 'sms', 'push']\n"
            "class Message:\n"
            "    channel: Channel\n"
        ),
        "src/handlers.py": (
            "from collections.abc import Callable\n"
            "from models import Channel\n"
            "def email(): pass\n"
            "def sms(): pass\n"
            "def push(): pass\n"
            "HANDLERS: dict[Channel, Callable[[], None]] = {\n"
            "    'email': email, 'sms': sms, 'push': push\n"
            "}\n"
        ),
        "src/workflow.py": (
            "from models import Message\n"
            "def deliver(message: Message):\n"
            "    if message.channel == 'push':\n"
            "        return 'background'\n"
            "    return 'foreground'\n"
        ),
    }

    assert report_from(tmp_path, files) == [
        (
            "src/workflow.py:2: deliver branches on Channel outside its "
            "handler registry in src/handlers.py"
        )
    ]


def test_allows_python_branch_in_registry_module(tmp_path: Path) -> None:
    files = {
        "src/policy.py": (
            "from collections.abc import Callable\n"
            "from typing import Literal\n"
            "Channel = Literal['email', 'sms', 'push']\n"
            "def email(): pass\n"
            "def sms(): pass\n"
            "def push(): pass\n"
            "HANDLERS: dict[Channel, Callable[[], None]] = {\n"
            "    'email': email, 'sms': sms, 'push': push\n"
            "}\n"
            "def urgent(channel: Channel):\n"
            "    return channel == 'push'\n"
        )
    }

    assert report_from(tmp_path, files) == []


def test_flags_python_protocol_with_one_method_per_variant(
    tmp_path: Path,
) -> None:
    files = {
        "src/visitor.py": (
            "from typing import Literal, Protocol\n"
            "ShapeKind = Literal['circle', 'square', 'triangle']\n"
            "class ShapeVisitor(Protocol):\n"
            "    def visit_circle(self): ...\n"
            "    def visit_square(self): ...\n"
            "    def visit_triangle(self): ...\n"
        )
    }

    assert report_from(tmp_path, files) == [
        (
            "src/visitor.py:3: ShapeVisitor requires one callback for every "
            "ShapeKind variant: circle, square, triangle"
        )
    ]


def test_allows_generic_python_visitor_method(tmp_path: Path) -> None:
    files = {
        "src/visitor.py": (
            "from typing import Literal, Protocol\n"
            "ShapeKind = Literal['circle', 'square', 'triangle']\n"
            "class ShapeVisitor(Protocol):\n"
            "    def visit(self, kind: ShapeKind): ...\n"
        )
    }

    assert report_from(tmp_path, files) == []

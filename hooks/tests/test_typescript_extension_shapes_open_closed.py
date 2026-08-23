from pathlib import Path

from typescript_finder_support import CHECKS, report_from

_FINDER = CHECKS / "open-closed" / "variant_dispatches.js"


def test_flags_closed_callback_visitor_for_literal_axis(
    tmp_path: Path,
) -> None:
    files = {
        "src/rendering.ts": (
            'type ShapeKind = "circle" | "square" | "triangle";\n'
            "type ShapeRenderers = {\n"
            "  readonly circle: () => string;\n"
            "  readonly square: () => string;\n"
            "  readonly triangle: () => string;\n"
            "};\n"
        ),
    }

    assert report_from(_FINDER, tmp_path, files) == [
        (
            "src/rendering.ts:2: ShapeRenderers requires one callback for "
            "every ShapeKind variant: circle, square, triangle"
        )
    ]


def test_allows_optional_callback_extensions(tmp_path: Path) -> None:
    files = {
        "src/rendering.ts": (
            'type ShapeKind = "circle" | "square" | "triangle";\n'
            "type ShapeRenderers = {\n"
            "  readonly circle?: () => string;\n"
            "  readonly square?: () => string;\n"
            "  readonly triangle?: () => string;\n"
            "};\n"
        ),
    }

    assert report_from(_FINDER, tmp_path, files) == []


def test_flags_closed_method_interface_for_literal_axis(
    tmp_path: Path,
) -> None:
    files = {
        "src/visitor.ts": (
            'type EventKind = "created" | "updated" | "deleted";\n'
            "interface EventVisitor {\n"
            "  created(): void;\n"
            "  updated(): void;\n"
            "  deleted(): void;\n"
            "}\n"
        ),
    }

    assert report_from(_FINDER, tmp_path, files) == [
        (
            "src/visitor.ts:2: EventVisitor requires one callback for every "
            "EventKind variant: created, deleted, updated"
        )
    ]


def test_flags_concrete_dependency_owned_by_abstract_factory(
    tmp_path: Path,
) -> None:
    files = {
        "src/factory.ts": (
            "interface Transport { send(): void }\n"
            "class SocketClient {}\n"
            "class TransportFactory {\n"
            "  private readonly client = new SocketClient();\n"
            "  create(): Transport { throw new Error(); }\n"
            "}\n"
        ),
    }

    assert report_from(_FINDER, tmp_path, files) == [
        (
            "src/factory.ts:3: TransportFactory leaks concrete dependencies "
            "while creating Transport: SocketClient"
        )
    ]


def test_allows_dependency_injected_into_abstract_factory(
    tmp_path: Path,
) -> None:
    files = {
        "src/factory.ts": (
            "interface Transport { send(): void }\n"
            "interface Client { request(): void }\n"
            "class TransportFactory {\n"
            "  constructor(private readonly client: Client) {}\n"
            "  create(): Transport { throw new Error(); }\n"
            "}\n"
        ),
    }

    assert report_from(_FINDER, tmp_path, files) == []

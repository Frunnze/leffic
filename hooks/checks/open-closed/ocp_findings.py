import ast
from typing import NamedTuple

MAXIMUM_VARIANTS = 2
FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
EQUALITY_NODES = (ast.Eq, ast.NotEq)
TYPE_EQUALITY_NODES = (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)


class VariantDispatch(NamedTuple):
    path: str
    line_number: int
    function_name: str
    subject: str
    variants: tuple[str, ...]


class ConcreteTypeDispatch(NamedTuple):
    path: str
    line_number: int
    function_name: str
    subject: str
    concrete_types: tuple[str, ...]


class CentralConstruction(NamedTuple):
    path: str
    line_number: int
    function_name: str
    subject: str
    implementations: tuple[str, ...]


class ScatteredVariantDispatch(NamedTuple):
    path: str
    line_number: int
    function_name: str
    subject: str
    variants: tuple[str, ...]
    function_count: int


class ClosedFactory(NamedTuple):
    path: str
    line_number: int
    function_name: str
    abstraction: str
    implementations: tuple[str, ...]


class ConcreteFactoryDependency(NamedTuple):
    path: str
    line_number: int
    factory_name: str
    abstraction: str
    dependencies: tuple[str, ...]


class RegistryEscape(NamedTuple):
    path: str
    line_number: int
    function_name: str
    axis: str
    registry_paths: tuple[str, ...]


class FragmentedRegistry(NamedTuple):
    path: str
    line_number: int
    axis: str
    registry_names: tuple[str, ...]
    file_count: int


class ClosedVisitor(NamedTuple):
    path: str
    line_number: int
    visitor_name: str
    axis: str
    variants: tuple[str, ...]


Finding = (
    VariantDispatch
    | ConcreteTypeDispatch
    | CentralConstruction
    | ScatteredVariantDispatch
    | ClosedFactory
    | ConcreteFactoryDependency
    | RegistryEscape
    | FragmentedRegistry
    | ClosedVisitor
)

from ocp_findings import ClosedVisitor, FragmentedRegistry, RegistryEscape
from python_registries import fragmented_registries, registries_in
from python_registry_escapes import registry_escapes
from python_structure_types import axes_in, class_fields, modules_from
from python_visitors import closed_visitors


def structural_findings(
    paths: list[str],
) -> list[ClosedVisitor | FragmentedRegistry | RegistryEscape]:
    modules = modules_from(paths)
    axes = axes_in(modules)
    fields = class_fields(modules, axes)
    registries = registries_in(modules, axes)

    return [
        *fragmented_registries(registries),
        *registry_escapes(modules, axes, fields, registries),
        *closed_visitors(modules, axes),
    ]

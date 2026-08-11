from dataclasses import dataclass


@dataclass(frozen=True)
class StudyUnitSource:
    kind: str | None
    reference: str | None

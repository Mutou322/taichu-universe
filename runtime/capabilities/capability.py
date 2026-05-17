"""Capability data model representing a named skill with a score."""

from dataclasses import dataclass


@dataclass
class Capability:
    """A named capability with an associated proficiency score."""

    name: str

    score: float = 1.0

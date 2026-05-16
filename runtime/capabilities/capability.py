# runtime/capabilities/capability.py

from dataclasses import dataclass


@dataclass
class Capability:

    name: str

    score: float = 1.0

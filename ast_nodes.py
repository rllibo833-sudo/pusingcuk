"""Node AST untuk bahasa Pusingcuk."""
from dataclasses import dataclass, field


@dataclass
class Node:
    kind: str
    fields: dict = field(default_factory=dict)
    line: int = 0

    def __getattr__(self, name):
        if name in self.fields:
            return self.fields[name]
        raise AttributeError(name)


def node(kind, line=0, **fields):
    return Node(kind, fields, line)

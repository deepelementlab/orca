"""Citation data model."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Citation:
    """引用记录."""
    source_id: str
    context: str
    relevance_score: float = 0.0
    quote: str = ""

    def to_dict(self) -> dict:
        return {"source_id": self.source_id, "context": self.context,
                "relevance_score": self.relevance_score, "quote": self.quote}

    @classmethod
    def from_dict(cls, data: dict) -> Citation:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

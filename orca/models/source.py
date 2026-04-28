"""Research source data model."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


def _parse_date(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass
    if len(value) == 4 and value.isdigit():
        return datetime(int(value), 1, 1)
    return None


@dataclass
class Source:
    """研究来源 (论文、网页、报告等)."""
    id: str
    title: str
    authors: list[str] = field(default_factory=list)
    url: str = ""
    source_type: str = "web"  # "arxiv" | "alphaXiv" | "web" | "semantic_scholar"
    published_date: Optional[datetime] = None
    abstract: Optional[str] = None
    citation_count: Optional[int] = None
    pdf_url: Optional[str] = None
    doi: Optional[str] = None
    keywords: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "authors": self.authors,
                "url": self.url, "source_type": self.source_type,
                "published_date": self.published_date.isoformat() if self.published_date else None,
                "abstract": self.abstract, "citation_count": self.citation_count,
                "pdf_url": self.pdf_url, "doi": self.doi, "keywords": self.keywords}

    @classmethod
    def from_dict(cls, data: dict) -> Source:
        d = dict(data)
        if isinstance(d.get("published_date"), str):
            d["published_date"] = _parse_date(d["published_date"])
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

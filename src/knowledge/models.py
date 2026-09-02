from dataclasses import dataclass

@dataclass
class KnowledgeEntry:
    id: int | None
    name: str
    normalized_name: str
    category: str
    description: str
    source: str | None = None
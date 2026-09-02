import json
from pathlib import Path

from src.knowledge.database import create_database
from src.knowledge.repository import KnowledgeRepository


DATA_PATH = Path("data/knowledge.json")


def seed_database():
    create_database()

    repository = KnowledgeRepository()

    with open(DATA_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    for entry in data:
        entry_id = repository.add_entry(
            entry["name"],
            entry["category"],
            entry["description"],
            entry.get("source")
        )

        for alias in entry.get("aliases", []):
            repository.add_alias(entry_id, alias)


if __name__ == "__main__":
    seed_database()
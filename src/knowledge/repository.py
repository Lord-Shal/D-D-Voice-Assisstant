from src.knowledge.database import get_connection
from src.knowledge.models import KnowledgeEntry
from src.knowledge.normalizer import normalize_term


class KnowledgeRepository:
    def add_entry(self, name, category, description, source=None):
        normalized_name = normalize_term(name)

        connection = get_connection()

        cursor = connection.execute("""
            INSERT OR IGNORE INTO entries (
                name,
                normalized_name,
                category,
                description,
                source
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            normalized_name,
            category,
            description,
            source
        ))

        connection.commit()

        if cursor.lastrowid:
            entry_id = cursor.lastrowid
        else:
            row = connection.execute("""
                SELECT id
                FROM entries
                WHERE normalized_name = ?
            """, (normalized_name,)).fetchone()

            entry_id = row["id"]

        connection.close()

        return entry_id

    def add_alias(self, entry_id, alias):
        normalized_alias = normalize_term(alias)

        connection = get_connection()

        connection.execute("""
            INSERT OR IGNORE INTO aliases (
                entry_id,
                alias,
                normalized_alias
            )
            VALUES (?, ?, ?)
        """, (
            entry_id,
            alias,
            normalized_alias
        ))

        connection.commit()
        connection.close()

    def get_by_name(self, name):
        normalized_name = normalize_term(name)

        connection = get_connection()

        row = connection.execute("""
            SELECT *
            FROM entries
            WHERE normalized_name = ?
        """, (normalized_name,)).fetchone()

        connection.close()

        if row is None:
            return None

        return KnowledgeEntry(
            id=row["id"],
            name=row["name"],
            normalized_name=row["normalized_name"],
            category=row["category"],
            description=row["description"],
            source=row["source"]
        )

    def get_by_alias(self, alias):
        normalized_alias = normalize_term(alias)

        connection = get_connection()

        row = connection.execute("""
            SELECT entries.*
            FROM aliases
            JOIN entries ON aliases.entry_id = entries.id
            WHERE aliases.normalized_alias = ?
        """, (normalized_alias,)).fetchone()

        connection.close()

        if row is None:
            return None

        return KnowledgeEntry(
            id=row["id"],
            name=row["name"],
            normalized_name=row["normalized_name"],
            category=row["category"],
            description=row["description"],
            source=row["source"]
        )

    def lookup(self, term):
        entry = self.get_by_name(term)

        if entry is not None:
            return entry

        return self.get_by_alias(term)

    def get_by_category(self, category):
        normalized_category = normalize_term(category)

        connection = get_connection()

        rows = connection.execute("""
            SELECT *
            FROM entries
            WHERE category = ?
        """, (normalized_category,)).fetchall()

        connection.close()

        return [
            KnowledgeEntry(
                id=row["id"],
                name=row["name"],
                normalized_name=row["normalized_name"],
                category=row["category"],
                description=row["description"],
                source=row["source"]
            )
            for row in rows
        ]

    def search(self, query):
        normalized_query = normalize_term(query)

        connection = get_connection()

        rows = connection.execute("""
            SELECT DISTINCT entries.*
            FROM entries
            LEFT JOIN aliases ON aliases.entry_id = entries.id
            WHERE entries.normalized_name LIKE ?
            OR aliases.normalized_alias LIKE ?
        """, (
            f"%{normalized_query}%",
            f"%{normalized_query}%"
        )).fetchall()

        connection.close()

        return [
            KnowledgeEntry(
                id=row["id"],
                name=row["name"],
                normalized_name=row["normalized_name"],
                category=row["category"],
                description=row["description"],
                source=row["source"]
            )
            for row in rows
        ]
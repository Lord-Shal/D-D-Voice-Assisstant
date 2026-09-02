from src.knowledge.repository import KnowledgeRepository


class KnowledgeBase:
    def __init__(self):
        self.repository = KnowledgeRepository()

    def lookup(self, term):
        return self.repository.lookup(term)

    def search(self, query):
        return self.repository.search(query)

    def get_by_category(self, category):
        return self.repository.get_by_category(category)
from src.knowledge.knowledge_base import KnowledgeBase


knowledge = KnowledgeBase()

print("Fireball:")
print(knowledge.lookup("fireball"))

print("\nFireball uppercase:")
print(knowledge.lookup("FIREBALL"))

print("\nCritical Hit via alias:")
print(knowledge.lookup("crit"))

print("\nSearch:")
print(knowledge.search("crit"))

print("\nSpells:")
print(knowledge.get_by_category("spell"))
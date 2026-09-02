import re

def normalize_term(term):
    term = term.lower().strip()
    term = re.sub(r"[-_]", " ", term)
    term = re.sub(r"\s+", " ", term)
    return term
KNOWN_TABLES = {"KNA1", "VBAK", "VBAP"}

def extract_tables_from_answer(answer: str):
    return [t for t in KNOWN_TABLES if t in answer]

def is_refusal(answer: str):
    refusal_phrases = [
        "could not find",
        "no evidence",
        "cannot determine",
        "insufficient information"
    ]
    return any(p in answer.lower() for p in refusal_phrases)

def precision_recall(predicted, expected):
    if not predicted and not expected:
        return 1.0, 1.0
    if not predicted:
        return 0.0, 0.0

    p = len(set(predicted) & set(expected)) / len(predicted)
    r = len(set(predicted) & set(expected)) / len(expected) if expected else 1.0
    return p, r

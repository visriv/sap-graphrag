import random

BASE_QUERIES = [
    {
        "templates": [
            "What tables store customer data?",
            "Which SAP tables contain customer information?",
            "Where is customer master data stored?",
            "Which tables represent customers?"
        ],
        "task_type": "entity_lookup",
        "expected": {
            "tables": ["KNA1"],
            "relationships": [],
            "answerable": True
        }
    },
    {
        "templates": [
            "How is VBAK connected to KNA1?",
            "What is the relationship between sales orders and customers?",
            "How does VBAK reference customer data?",
            "Explain the link between VBAK and KNA1."
        ],
        "task_type": "relationship",
        "expected": {
            "tables": ["VBAK", "KNA1"],
            "relationships": [["VBAK", "KNA1"]],
            "answerable": True
        }
    },
    {
        "templates": [
            "What tables depend on KNA1?",
            "Which tables reference the customer master?",
            "What is impacted if customer data changes?",
            "Which tables rely on KNA1?"
        ],
        "task_type": "impact",
        "expected": {
            "tables": ["VBAK"],
            "relationships": [["VBAK", "KNA1"]],
            "answerable": True
        }
    },
    {
        "templates": [
            "Is there a direct join between VBAP and KNA1?",
            "Can VBAP be joined directly with customer data?",
            "Does VBAP reference KNA1 without VBAK?",
            "Is there a foreign key from VBAP to KNA1?"
        ],
        "task_type": "negative_relationship",
        "expected": {
            "tables": [],
            "relationships": [],
            "answerable": False
        }
    }
]


def generate_dataset(num_samples: int):
    dataset = []

    for i in range(num_samples):
        base = random.choice(BASE_QUERIES)
        query = random.choice(base["templates"])

        dataset.append({
            "query_id": f"Q{i:03d}",
            "query": query,
            "task_type": base["task_type"],
            "expected": base["expected"]
        })

    return dataset


# File: backend/tests/test_queries.py

test_queries = [
    "What tables contain customer information?",
    "How are sales orders related to customers?",
    "Show me all fields in VBAK table",
    "What would be affected if I change customer master data?",
    "Explain the order-to-cash flow"
]

for query in test_queries:
    result = processor.process(query)
    print(f"Q: {query}")
    print(f"A: {result['answer']}\\n")
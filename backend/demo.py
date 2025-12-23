# File: demo.py

from src.rag.query_processor import GraphRAGProcessor

import os
# backend/src/demo.py
from src.graph.neo4j_client import Neo4jClient

client = Neo4jClient()
print(client.run("RETURN 'Neo4j OK' AS msg"))



processor = GraphRAGProcessor(
    neo4j_uri=os.getenv("NEO4J_URI"),
    neo4j_user=os.getenv("NEO4J_USER"),
    neo4j_password=os.getenv("NEO4J_PASSWORD"),
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
)

print("=== SAP GraphRAG Agent Demo ===\\n")

# Demo 1: Simple table query
print("Query 1: What tables store customer data?")
result = processor.process("What tables store customer data?")
print(result['answer'])
print("\\n" + "="*50 + "\\n")

# Demo 2: Relationship query
print("Query 2: How is VBAK connected to KNA1?")
result = processor.process("How is VBAK connected to KNA1?")
print(result['answer'])
print("\\n" + "="*50 + "\\n")

# Demo 3: Impact analysis
print("Query 3: What depends on customer table?")
result = processor.process("What tables depend on KNA1?")
print(result['answer'])
# backend/src/graph/neo4j_client.py
import os
from neo4j import GraphDatabase

class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = None

    def connect(self):
        if self.driver is None:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )

    def close(self):
        if self.driver:
            self.driver.close()

    def run(self, query, params=None):
        self.connect()
        with self.driver.session() as session:
            return session.run(query, params or {}).data()

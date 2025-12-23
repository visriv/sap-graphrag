from langchain_anthropic import ChatAnthropic
from neo4j import GraphDatabase
import json
import re


class GraphRAGProcessor:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password, anthropic_api_key):
        self.graph_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            # api_key=anthropic_api_key,
            max_tokens=2000
        )
    
    def extract_entities(self, query):
        """Use LLM to extract table names and entities from query"""
        prompt = f"""
        Extract SAP table names and entities from this query: "{query}"
        
        Return as JSON:
        {{
            "tables": ["TABLE1", "TABLE2"],
            "entities": ["customer", "order"],
            "intent": "relationship|impact|data_flow"
        }}
        """
        
        response = self.llm.invoke(prompt)
        # Parse JSON from response
        return response.content
    
    def retrieve_subgraph(self, entities):
        """Query Neo4j for relevant subgraph"""
        with self.graph_driver.session() as session:
            # Example: Get all tables and their relationships
            result = session.run("""
                MATCH (t1:Table)-[r:RELATES_TO]->(t2:Table)
                WHERE t1.name IN $table_names OR t2.name IN $table_names
                RETURN t1, r, t2
            """, table_names=entities['tables'])
            
            return [record.data() for record in result]
    
    def generate_response(self, query, graph_context):
        """Use LLM to reason over graph and generate answer"""
        
        context = self._format_graph_context(graph_context)
        
        prompt = f"""
        You are an SAP HANA expert. Answer this question using the schema information provided.
        
        Question: {query}
        
        Schema Context:
        {context}
        
        Provide:
        1. A clear answer
        2. Relevant table names
        3. Relationship explanations
        4. Field-level details
        """
        
        response = self.llm.invoke(prompt)
        return response.content
    
    def _format_graph_context(self, graph_data):
        """Format graph data into readable context for LLM"""
        formatted = []
        for record in graph_data:
            t1 = record.get('t1', {})
            r = record.get('r', {})
            t2 = record.get('t2', {})
            formatted.append(
                f"Table: {t1.get('name')} ({t1.get('description')})\\n"
                f"  → Related to: {t2.get('name')} via {r.get('via')}\\n"
                f"  Relationship: {r.get('description')}\\n"
            )
        return "\\n".join(formatted)
    
    def process(self, query):
        """Main pipeline"""
        # 1. Extract entities from query

        raw = self.extract_entities(query)

        # 1. Extract JSON from ```json ... ``` if present
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError(f"LLM did not return JSON:\n{raw}")

        entities = json.loads(match.group())

        
        # 2. Retrieve relevant subgraph
        graph_context = self.retrieve_subgraph(entities)
        
        # 3. Generate response
        answer = self.generate_response(query, graph_context)
        
        return {
            "query": query,
            "entities": entities,
            "graph_context": graph_context,
            "answer": answer
        }
from neo4j import GraphDatabase
import json

class GraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_schema_graph(self, schema_file):
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        
        with self.driver.session() as session:
            # Create table nodes
            for table in schema['tables']:
                session.run("""
                    CREATE (t:Table {
                        name: $name,
                        description: $description,
                        type: $type,
                        documentation: $documentation
                    })
                """, 
                name=table['name'],
                description=table['description'],
                type=table['type'],
                documentation=table['documentation'])
                
                # Create field nodes
                for field in table['fields']:
                    session.run("""
                        MATCH (t:Table {name: $table_name})
                        CREATE (f:Field {
                            name: $field_name,
                            type: $field_type,
                            is_key: $is_key,
                            description: $description
                        })
                        CREATE (t)-[:HAS_FIELD]->(f)
                    """,
                    table_name=table['name'],
                    field_name=field['name'],
                    field_type=field['type'],
                    is_key=field['key'],
                    description=field['description'])
            
            # Create relationships
            for rel in schema['relationships']:
                session.run("""
                    MATCH (from:Table {name: $from})
                    MATCH (to:Table {name: $to})
                    CREATE (from)-[:RELATES_TO {
                        via: $via,
                        type: $type,
                        description: $description
                    }]->(to)
                """,
                from_name=rel['from'],
                to_name=rel['to'],
                via=rel['via'],
                type=rel['type'],
                description=rel['description'])

# # Usage
# builder = GraphBuilder("bolt://localhost:7687", "neo4j", "password")
# builder.create_schema_graph("data/mock_sap_schema.json")
# builder.close()
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.rag.query_processor import GraphRAGProcessor
import os

app = FastAPI(title="SAP GraphRAG API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processor
processor = GraphRAGProcessor(
    neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
    neo4j_password=os.getenv("NEO4J_PASSWORD", "password"),
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    answer: str
    tables: list[str]
    relationships: list[dict]

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        result = processor.process(request.query)
        return QueryResponse(
            query=result['query'],
            answer=result['answer'],
            tables=result['entities'].get('tables', []),
            relationships=result.get('graph_context', [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schema")
async def get_schema():
    """Return available tables"""
    with processor.graph_driver.session() as session:
        result = session.run("MATCH (t:Table) RETURN t")
        tables = [record['t'] for record in result]
    return {"tables": tables}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
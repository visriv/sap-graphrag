# SAP GraphRAG Agent Demo

This project demonstrates a **GraphRAG-based AI agent** for SAP schema reasoning, and compares it against a **Plain RAG baseline**.

It includes:
- Neo4j-backed SAP schema graph
- GraphRAG vs PlainRAG reasoning
- Quantitative evaluation (precision / recall) #(TODO: need to fix bugs)
- Streamlit visualization of intermediate reasoning steps #(TODO: need to fix bugs)

---

## Architecture Overview

```
User Query
   │
   ├── Plain RAG
   │     └── LLM + schema text
   │
   └── Graph RAG
         ├── Entity extraction (LLM)
         ├── Subgraph retrieval (Neo4j)
         └── Grounded reasoning (LLM)
```

GraphRAG constrains the LLM using **explicit schema structure**, reducing hallucinations.

---

## Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Neo4j (runs via Docker)
- Anthropic API key (Claude)

---

## Setup (From Scratch)

### 1. Clone the repository

```bash
git clone https://github.com/visriv/sap-graphrag.git
cd sap-graphrag
```

---

### 2. Set environment variables

Create a `.env` file:

```env
ANTHROPIC_API_KEY=your_api_key_here
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

---

### 3. Start services

```bash
docker compose up --build
```

This starts:
- Neo4j (with APOC)
- Backend API container

Neo4j UI: http://localhost:7474  
Credentials: `neo4j / password`

---

### 4. Load SAP schema into Neo4j

Inside the backend container:

```bash
docker exec -it sap-backend python src/graph/load_schema.py
```

(This uses `data/mock_sap_schema.json`)

---

## Running the Demo

### GraphRAG demo

```bash
docker exec -it sap-backend python demo.py
```

## Evaluation

### Run quantitative evaluation

```bash
docker exec -it sap-backend python src/eval/run_eval.py
```

Results are saved to:

```
runs/<timestamp>/results.tsv
```


---

### Streamlit reasoning visualization
(TODO: need to fix bugs)
```bash
streamlit run backend/src/streamlit_compare.py
```

This shows:
- Plain RAG vs Graph RAG answers
- Extracted entities
- Retrieved graph context
- Grounded vs hallucinated tables

---



---

## Dataset

Evaluation queries are generated from:

```
src/eval/dataset.py
```

Each example includes:
- Query
- Task type (entity / relationship / impact)
- Expected tables
- Expected answerability

This enables deterministic evaluation.

---


## TODO:
- [] : dynamically generate the graph
- [] : frontend/streamlit
- [] : precision recall calculation fix

## Extending This Project


Ideas:
- Dynamically constructing the graph (instead of a synthetic graph we used)
- Larger SAP schemas
- Query decomposition
- Multi-hop graph reasoning


---

## License

MIT

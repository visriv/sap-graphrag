import json
import os
import re
import streamlit as st

from rag.query_processor import GraphRAGProcessor
from rag.plain_rag import PlainRAGProcessor
from eval.dataset import generate_dataset


# -----------------------------
# Helpers
# -----------------------------
KNOWN_TABLES = {"KNA1", "VBAK", "VBAP"}


def highlight_tables(text, tables):
    for t in tables:
        text = re.sub(
            rf"\b{t}\b",
            f":green[{t}]",
            text
        )
    return text


def extract_tables_from_text(text):
    return [t for t in KNOWN_TABLES if t in text]


def flatten_graph_context(graph_context):
    if not graph_context:
        return "No graph context retrieved."
    return json.dumps(graph_context, indent=2)


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(layout="wide")
st.title("🧠 PlainRAG vs GraphRAG — Step-by-Step Comparison")

st.markdown("""
This demo visualizes **intermediate reasoning steps** for:
- Plain RAG (LLM + schema text)
- Graph RAG (LLM + Neo4j schema graph)

Focus is on **grounding, hallucinations, and evidence flow**.
""")

# -----------------------------
# Load agents
# -----------------------------
dataset = generate_dataset(num_samples=3)

with open("data/mock_sap_schema.json") as f:
    schema_json = json.load(f)

schema_text = "\n".join(
    f"{t['name']}: {t['description']}" for t in schema_json["tables"]
)

graph_agent = GraphRAGProcessor(
    os.getenv("NEO4J_URI"),
    os.getenv("NEO4J_USER"),
    os.getenv("NEO4J_PASSWORD"),
    os.getenv("ANTHROPIC_API_KEY"),
)

plain_agent = PlainRAGProcessor(schema_text)

# -----------------------------
# Query selector
# -----------------------------
queries = {ex["query_id"]: ex for ex in dataset}
selected_id = st.selectbox("Select a query", list(queries.keys()))
query = queries[selected_id]["query"]

st.markdown(f"### 🔍 Query\n> **{query}**")

# -----------------------------
# Run agents
# -----------------------------
with st.spinner("Running agents..."):
    graph_result = graph_agent.process(query)
    plain_result = plain_agent.process(query)

# -----------------------------
# Layout
# -----------------------------
col1, col2 = st.columns(2)

# -----------------------------
# Plain RAG Panel
# -----------------------------
with col1:
    st.subheader("📄 Plain RAG")

    answer = plain_result["answer"]
    tables = extract_tables_from_text(answer)

    st.markdown("**Answer**")
    st.markdown(highlight_tables(answer, tables))

    st.markdown("**Tables Mentioned**")
    if tables:
        st.success(", ".join(tables))
    else:
        st.warning("No tables mentioned")

    st.markdown("**Reasoning**")
    st.info("LLM reasons directly from schema text. No structural constraints.")

# -----------------------------
# Graph RAG Panel
# -----------------------------
with col2:
    st.subheader("🧩 Graph RAG")

    answer = graph_result["answer"]
    tables = extract_tables_from_text(answer)

    st.markdown("**Extracted Entities**")
    st.code(graph_result["entities"], language="json")

    st.markdown("**Retrieved Graph Context**")
    st.code(flatten_graph_context(graph_result["graph_context"]), language="json")

    st.markdown("**Answer**")
    st.markdown(highlight_tables(answer, tables))

    st.markdown("**Tables Mentioned**")
    if tables:
        st.success(", ".join(tables))
    else:
        st.warning("No tables mentioned")

    st.markdown("**Reasoning**")
    st.info("LLM reasons only over retrieved graph evidence.")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("GraphRAG constrains reasoning via explicit schema structure. Plain RAG relies on probabilistic inference.")

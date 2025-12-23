import os
import csv
import json
from datetime import datetime

from src.eval.dataset import generate_dataset
from src.eval.evaluator import extract_tables_from_answer, is_refusal
from src.rag.query_processor import GraphRAGProcessor
from src.rag.plain_rag import PlainRAGProcessor


def flatten_schema_for_rag(schema_json):
    lines = []
    for t in schema_json["tables"]:
        lines.append(f"Table {t['name']}: {t['description']}")
        for f in t["fields"]:
            lines.append(f"  - {f['name']}: {f['description']}")
    return "\n".join(lines)


def run_evaluation(num_samples: int):
    dataset = generate_dataset(num_samples)

    # Load schema for plain RAG
    with open("data/mock_sap_schema.json") as f:
        schema_json = json.load(f)

    schema_text = flatten_schema_for_rag(schema_json)

    agents = {
        "graph_rag": GraphRAGProcessor(
            os.getenv("NEO4J_URI"),
            os.getenv("NEO4J_USER"),
            os.getenv("NEO4J_PASSWORD"),
            os.getenv("ANTHROPIC_API_KEY"),
        ),
        "plain_rag": PlainRAGProcessor(schema_text),
    }

    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_dir = f"runs/{run_id}"
    os.makedirs(out_dir, exist_ok=True)

    rows = []

    # Aggregation buckets
    stats = {
        agent: {"TP": 0, "FP": 0, "FN": 0}
        for agent in agents
    }

    for agent_name, agent in agents.items():
        for ex in dataset:
            print(f"[{agent_name}] {ex['query_id']} - {ex['query']}")

            result = agent.process(ex["query"])
            answer = result["answer"]

            predicted = set(extract_tables_from_answer(answer))
            expected = set(ex["expected"]["tables"])

            # Update aggregation stats
            stats[agent_name]["TP"] += len(predicted & expected)
            stats[agent_name]["FP"] += len(predicted - expected)
            stats[agent_name]["FN"] += len(expected - predicted)

            rows.append({
                "run_id": run_id,
                "agent": agent_name,
                "query_id": ex["query_id"],
                "task_type": ex["task_type"],
                "query": ex["query"],
                "predicted_tables": ",".join(predicted),
                "expected_tables": ",".join(expected),
                "predicted_answerable": not is_refusal(answer),
                "expected_answerable": ex["expected"]["answerable"],
            })

    # Add summary rows
    for agent_name, s in stats.items():
        tp, fp, fn = s["TP"], s["FP"], s["FN"]

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        rows.append({
            "run_id": run_id,
            "agent": agent_name,
            "query_id": "ALL",
            "task_type": "SUMMARY",
            "query": "ALL",
            "predicted_tables": "",
            "expected_tables": "",
            "predicted_answerable": "",
            "expected_answerable": "",
            "precision": round(precision, 3),
            "recall": round(recall, 3),
        })

    out_path = f"{out_dir}/results.tsv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=rows[0].keys(),
            delimiter="\t"
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved evaluation results to {out_path}")


if __name__ == "__main__":
    run_evaluation(num_samples=20)

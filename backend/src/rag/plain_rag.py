from langchain_anthropic import ChatAnthropic
import os

class PlainRAGProcessor:
    def __init__(self, schema_text: str):
        self.schema_text = schema_text
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            max_tokens=1000
        )

    def process(self, query: str):
        prompt = f"""
You are an SAP HANA expert.

Schema documentation:
{self.schema_text}

Question:
{query}

Answer concisely.
If you are unsure, say so.
"""
        response = self.llm.invoke(prompt)
        return {
            "answer": response.content
        }

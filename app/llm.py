import os

import requests


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "mistral:latest",
)


def generate_answer_with_ollama(query: str, context: str) -> str:
    """
    Generate an answer using a local Ollama model.

    The model must answer only from the provided document context.
    """
    prompt = f"""
You are an assistant that answers questions about invoices.

Use ONLY the information provided in the context.

If the answer is not explicitly present in the context, reply exactly:
I cannot find this information in the document.

Return only the answer.
Do not explain your reasoning.

Context:
{context}

Question:
{query}

Answer:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["response"].strip()
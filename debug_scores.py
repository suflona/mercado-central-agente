"""
Script de diagnóstico: muestra el score de similitud de TODOS los chunks
para una pregunta dada, para calibrar MIN_SCORE con datos reales.

Uso:
    python debug_scores.py "¿cuánto cuesta el arroz Diana?"
"""
import os
import sys
import json
import numpy as np
import cohere

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
INDEX_PATH = os.path.join(BASE_DIR, "vectorstore", "index.json")
EMBED_MODEL = "embed-multilingual-v3.0"


def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main():
    question = sys.argv[1] if len(sys.argv) > 1 else "¿cuánto cuesta el arroz Diana?"

    api_key = os.environ.get("COHERE_API_KEY")
    co = cohere.Client(api_key)

    with open(INDEX_PATH, encoding="utf-8") as f:
        data = json.load(f)
    records = data["records"]

    q_embed = co.embed(
        texts=[question], model=EMBED_MODEL, input_type="search_query"
    ).embeddings[0]
    q_vec = np.array(q_embed)

    scored = []
    for r in records:
        score = cosine_similarity(q_vec, np.array(r["embedding"]))
        scored.append((score, r["source_file"], r["page"], r["text"][:70]))

    scored.sort(reverse=True)

    print(f"\nPregunta: {question}\n")
    print(f"{'SCORE':>7}  FUENTE / FILA  -  TEXTO")
    print("-" * 90)
    for score, source, page, text in scored[:15]:
        print(f"{score:7.3f}  {source} / {page}  -  {text}")


if __name__ == "__main__":
    main()

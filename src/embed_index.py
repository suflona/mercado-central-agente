"""
Genera embeddings de cada chunk usando la API de Cohere y los guarda en
un solo archivo (vectorstore/index.json). No usamos una base de datos
vectorial externa (como Chroma) para mantener el proyecto simple: con
pocos documentos, guardar los vectores en un archivo y comparar con
similitud coseno en memoria es más que suficiente.

Antes de embeber, siempre vuelve a correr ingest.py para asegurar que
data/processed/chunks.jsonl esté sincronizado con lo que haya en
data/raw/ (por si el CSV o los PDF cambiaron).

Requiere la variable de entorno COHERE_API_KEY (gratis en
https://dashboard.cohere.com/api-keys).
"""
import os
import json
import cohere
import ingest

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
CHUNKS_PATH = os.path.join(BASE_DIR, "data", "processed", "chunks.jsonl")
INDEX_PATH = os.path.join(BASE_DIR, "vectorstore", "index.json")

EMBED_MODEL = "embed-multilingual-v3.0"  # soporta español nativamente
BATCH_SIZE = 96  # límite práctico por llamada a la API


def load_chunks():
    records = []
    with open(CHUNKS_PATH, encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return records


def build_index():
    api_key = os.environ.get("COHERE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Falta la variable de entorno COHERE_API_KEY. "
            "Consigue una gratis en https://dashboard.cohere.com/api-keys "
            "y expórtala antes de correr este script."
        )

    co = cohere.Client(api_key)

    # Siempre re-ingerimos primero, para que chunks.jsonl refleje el
    # contenido actual de data/raw/ (CSV/PDFs), sin depender de que
    # alguien haya corrido ingest.py manualmente antes.
    ingest.process_all()
    source_hash = ingest.compute_raw_hash()

    records = load_chunks()
    print(f"Cargados {len(records)} chunks desde {CHUNKS_PATH}")

    texts = [r["text"] for r in records]
    all_embeddings = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        response = co.embed(
            texts=batch,
            model=EMBED_MODEL,
            input_type="search_document",
        )
        all_embeddings.extend(response.embeddings)
        print(f"Embebidos {min(i + BATCH_SIZE, len(texts))}/{len(texts)} chunks...")

    for record, embedding in zip(records, all_embeddings):
        record["embedding"] = embedding

    payload = {"source_hash": source_hash, "records": records}

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)

    print(f"Índice guardado en {INDEX_PATH} (source_hash={source_hash[:12]}...)")


if __name__ == "__main__":
    build_index()

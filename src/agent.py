"""
Agente RAG de Mercado Central 24h.

Carga el índice generado por embed_index.py (chunks + sus embeddings),
busca los fragmentos más parecidos a la pregunta por similitud coseno
(con numpy, sin base de datos vectorial externa), y genera la respuesta
con el modelo de chat de Cohere, citando siempre la fuente.

Cada interacción se registra en logs/agent_log.jsonl para trazabilidad.
"""
import os
import json
import time
import numpy as np
import cohere
from datetime import datetime, timezone

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
INDEX_PATH = os.path.join(BASE_DIR, "vectorstore", "index.json")
LOG_PATH = os.path.join(BASE_DIR, "logs", "agent_log.jsonl")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

EMBED_MODEL = "embed-multilingual-v3.0"
CHAT_MODEL = "command-a-03-2025"
# TOP_K = None -> se calcula dinámicamente como len(self.records): siempre
# trae TODO el corpus indexado, sin importar cuántos chunks haya.
MIN_SCORE = 0.0  # sin filtro de score: con temperature=0 y corpus completo, el modelo decide qué es relevante

SYSTEM_PROMPT = """Eres el asistente virtual de Mercado Central 24h, un
supermercado colombiano abierto las 24 horas. Responde ÚNICAMENTE con base
en el contexto proporcionado, extraído de documentos oficiales de la
empresa (políticas, reglamento, FAQ e inventario). Si la respuesta no está
en el contexto, dilo explícitamente y sugiere contactar al área de
servicio al cliente. No inventes precios, políticas ni datos."""


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class MercadoCentralAgent:
    def __init__(self):
        api_key = os.environ.get("COHERE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Falta la variable de entorno COHERE_API_KEY. "
                "Consigue una gratis en https://dashboard.cohere.com/api-keys"
            )
        self.co = cohere.Client(api_key)

        with open(INDEX_PATH, encoding="utf-8") as f:
            self.records = json.load(f)

        self.embeddings = np.array([r["embedding"] for r in self.records])

    def _retrieve(self, question: str, k: int = None):
        if k is None:
            k = len(self.records)  # trae siempre todo el corpus indexado

        q_embed = self.co.embed(
            texts=[question], model=EMBED_MODEL, input_type="search_query"
        ).embeddings[0]
        q_vec = np.array(q_embed)

        scores = [cosine_similarity(q_vec, doc_vec) for doc_vec in self.embeddings]
        ranked = sorted(zip(self.records, scores), key=lambda x: x[1], reverse=True)
        top = [(r, s) for r, s in ranked[:k] if s >= MIN_SCORE]
        return top

    def _build_context(self, results):
        blocks = []
        for r, score in results:
            blocks.append(
                f"(Fuente: {r['source_file']}, pág/fila {r['page']})\n{r['text']}"
            )
        return "\n\n---\n\n".join(blocks)

    def ask(self, question: str) -> dict:
        start = time.time()
        results = self._retrieve(question)

        if not results:
            answer = ("No encontré información sobre esto en los documentos "
                       "disponibles. Te recomiendo contactar a servicio al "
                       "cliente en servicioalcliente@mercadocentral24h.com.co.")
            sources = []
        else:
            context = self._build_context(results)
            response = self.co.chat(
                model=CHAT_MODEL,
                preamble=SYSTEM_PROMPT,
                message=f"Contexto:\n{context}\n\nPregunta: {question}",
                temperature=0.0,
            )
            answer = response.text
            sources = [
                {"file": r["source_file"], "location": r["page"], "score": round(s, 3)}
                for r, s in results
            ]

        elapsed = round(time.time() - start, 3)
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "question": question,
            "answer": answer,
            "sources": sources,
            "response_time_seconds": elapsed,
            "model": CHAT_MODEL,
        }
        self._log(record)
        return record

    def _log(self, record: dict):
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    agent = MercadoCentralAgent()
    preguntas_demo = [
        "¿Cuál es el horario de atención del supermercado?",
        "¿Cuánto cuesta el arroz Diana de 500g?",
        "¿Puedo devolver una fruta si viene dañada?",
    ]
    for q in preguntas_demo:
        r = agent.ask(q)
        print(f"\nQ: {q}\nA: {r['answer']}\nFuentes: {r['sources']}\n")

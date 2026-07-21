"""
Extrae texto de los PDF y CSV en data/raw/, lo limpia, lo divide en
chunks con metadatos (archivo, página/fila, categoría) y guarda el
resultado en data/processed/chunks.jsonl.
"""
import os
import re
import json
import glob
import pandas as pd
import pdfplumber

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
CATEGORY = "Retail / Supermercado"


def clean_text(text: str) -> str:
    text = re.sub(r"\(cid:\d+\)", "-", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = end - overlap
    return chunks


def extract_pdf(path: str):
    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append((i, clean_text(text)))
    return pages


def extract_csv(path: str):
    df = pd.read_csv(path)
    rows_text = []
    for idx, row in df.iterrows():
        parts = [f"{col}: {row[col]}" for col in df.columns]
        rows_text.append((idx + 1, ". ".join(parts)))
    return rows_text


def process_all():
    records = []
    record_id = 0

    pdf_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.pdf")))
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        for page_num, page_text in extract_pdf(pdf_path):
            for chunk in chunk_text(page_text):
                record_id += 1
                records.append({
                    "id": f"chunk_{record_id:04d}",
                    "text": chunk,
                    "source_file": filename,
                    "source_type": "pdf",
                    "page": page_num,
                    "category": CATEGORY,
                })

    csv_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.csv")))
    for csv_path in csv_files:
        filename = os.path.basename(csv_path)
        for row_num, row_text in extract_csv(csv_path):
            record_id += 1
            records.append({
                "id": f"chunk_{record_id:04d}",
                "text": row_text,
                "source_file": filename,
                "source_type": "csv",
                "page": row_num,
                "category": CATEGORY,
            })

    out_path = os.path.join(PROCESSED_DIR, "chunks.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Procesados {len(pdf_files)} PDF y {len(csv_files)} CSV.")
    print(f"Generados {len(records)} chunks -> {out_path}")
    return records


if __name__ == "__main__":
    process_all()

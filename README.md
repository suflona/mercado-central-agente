# 🛒 Mercado Central 24h — Agente de IA (RAG)

Agente de inteligencia artificial que responde preguntas sobre horarios,
productos, precios, devoluciones y políticas internas de **Mercado Central
24h**, un supermercado colombiano ficticio abierto las 24 horas (proyecto
educativo — Challenge Alura Agente / Oracle Next Education).

> ⚠️ Mercado Central 24h es una entidad ficticia creada con fines
> educativos. No representa a ningún supermercado real.

## 📌 Descripción del proyecto

Un supermercado recibe todo el día preguntas repetitivas de clientes:
horarios, política de devoluciones, si tienen tal producto y a qué precio.
Este agente responde esas preguntas automáticamente, buscando en la
documentación oficial y citando siempre la fuente exacta.

Este proyecto es la versión **simple** del enfoque RAG: usa la API de
Cohere en vez de un modelo local, y guarda los vectores en un archivo
plano en vez de una base de datos vectorial — ideal para entender el
concepto sin tanta pieza en movimiento.

## 🏗️ Arquitectura

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐     ┌──────────────┐
│  data/raw   │ --> │   ingest.py  │ --> │ embed_index.py  │ --> │ vectorstore/ │
│ (PDF, CSV)  │     │ extracción + │     │ embeddings via  │     │  index.json  │
│             │     │   chunking   │     │  API Cohere     │     │              │
└─────────────┘     └──────────────┘     └────────────────┘     └──────┬───────┘
                                                                        │
┌─────────────┐     ┌──────────────┐     ┌────────────────┐            │
│  Streamlit  │ <-- │   agent.py   │ <-- │  Cohere Chat    │ <----------┘
│   (app.py)  │     │  RAG + logs  │     │  (command-a-03-2025)    │  similitud coseno (numpy)
└─────────────┘     └──────────────┘     └────────────────┘
```

**Flujo de una pregunta:**
1. El usuario escribe una pregunta.
2. Se genera su embedding con la API de Cohere.
3. Se compara (similitud coseno, con `numpy`) contra los embeddings ya
   guardados de cada chunk — sin base de datos vectorial externa.
4. Los 5 fragmentos más parecidos + la pregunta se envían al modelo de
   chat de Cohere (`command-a-03-2025`), con instrucciones de responder solo con
   ese contexto.
5. La respuesta se muestra con la fuente citada (archivo + página/fila).
6. Cada interacción se registra en `logs/agent_log.jsonl`.

## 🛠️ Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.11 |
| Embeddings y generación | API de Cohere (`embed-multilingual-v3.0`, `command-a-03-2025`) |
| Búsqueda por similitud | numpy (coseno, en memoria — sin vectorstore externo) |
| Extracción PDF | pdfplumber |
| Extracción CSV | pandas |
| Interfaz | Streamlit |
| Contenerización | Docker + Docker Compose |
| Deploy | Streamlit Community Cloud |

## 📂 Estructura del repositorio

```
mercado-central-agente/
├── data/
│   ├── raw/                # 3 PDFs (FAQ, devoluciones, reglamento) + CSV de inventario
│   └── processed/          # chunks.jsonl generado por ingest.py
├── src/
│   ├── ingest.py           # extracción + limpieza + chunking + metadatos
│   ├── embed_index.py      # embeddings vía Cohere + guardado en index.json
│   ├── agent.py            # recuperación (similitud coseno) + generación + logs
│   └── app.py               # interfaz Streamlit
├── scripts/
│   ├── generate_docs.py    # genera los PDF ficticios
│   └── generate_csv.py     # genera el inventario (CSV)
├── vectorstore/            # index.json (embeddings, no versionado)
├── logs/                   # logs de ejecución en JSON Lines
├── deploy/
│   └── OCI_DEPLOY.md       # guía de deploy en OCI
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🚀 Cómo ejecutar el proyecto localmente

### Requisitos previos
- Python 3.11+
- Una API key gratis de Cohere: https://dashboard.cohere.com/api-keys

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/mercado-central-agente.git
cd mercado-central-agente

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configurar tu API key de Cohere
export COHERE_API_KEY="tu_api_key_aqui"     # En Windows PowerShell: $env:COHERE_API_KEY="tu_api_key_aqui"

# 4. Procesar los documentos (extracción + chunking)
python src/ingest.py

# 5. Generar el índice de embeddings
python src/embed_index.py

# 6. Probar el agente por consola (opcional)
python src/agent.py

# 7. Levantar la interfaz web
streamlit run src/app.py
```

Abre `http://localhost:8501` en tu navegador.

## ☁️ Deploy

El deploy se intentó inicialmente en Oracle Cloud Infrastructure (OCI),
siguiendo la guía en [`deploy/OCI_DEPLOY.md`](deploy/OCI_DEPLOY.md). Sin
embargo, no fue posible completarlo por falta de disponibilidad de
capacidad Always Free en la región configurada. Como alternativa, el
deploy final se realizó en **Streamlit Community Cloud**, una opción
más liviana y directa para este tipo de aplicación (no requiere gestionar
una máquina virtual, solo conecta el repositorio de GitHub).

**App desplegada:**
- URL pública: **[mercado-central-agente.streamlit.app](https://mercado-central-agente.streamlit.app/)**

> La guía de deploy en OCI se conserva en [`deploy/OCI_DEPLOY.md`](deploy/OCI_DEPLOY.md)
> como referencia, por si se desea intentar ese camino en el futuro.

## 💬 Ejemplos de preguntas

| Pregunta | Fuente |
|---|---|
| ¿Cuál es el horario de atención? | FAQ |
| ¿Cuánto cuesta el arroz Diana de 500g? | Inventario (CSV) |
| ¿Puedo devolver una fruta si viene dañada? | Política de Atención al Cliente |
| ¿Hacen domicilios gratis? | FAQ |
| ¿Qué pasillo tiene los lácteos? | Inventario (CSV) |
| ¿Cómo funciona el programa de puntos? | FAQ |

## 🔒 Control de alucinación

Si la búsqueda no encuentra ningún fragmento con similitud suficiente
(`MIN_SCORE` en `agent.py`), el agente responde que no tiene esa
información en vez de inventar una respuesta.

## 👤 Autora

Proyecto desarrollado para el Challenge Alura Agente (Oracle Next
Education).

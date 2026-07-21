FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# La API key de Cohere se pasa en tiempo de ejecución (no se hardcodea
# en la imagen), por ejemplo: docker run -e COHERE_API_KEY=xxxx ...
ENV COHERE_API_KEY=""

EXPOSE 8501

CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

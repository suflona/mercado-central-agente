# Guía de Deploy en OCI (Oracle Cloud Infrastructure)

Este proyecto es más simple de desplegar que uno con LLM local, porque no
necesita correr Ollama — solo un contenedor que llama a la API de Cohere.

## 1. Crear la instancia (OCI Compute)

Igual que en la guía general: Compute → Instances → Create Instance,
imagen Ubuntu, shape `VM.Standard.A1.Flex` (Ampere, Always Free). Como este
proyecto no necesita correr un modelo pesado localmente, con **1-2 OCPU /
6-8 GB de RAM** sobra de sobra — no hace falta pedir los 4/24 completos.

## 2. Abrir el puerto 8501

Igual que antes: en la Security List de la VCN, agrega regla de ingreso
TCP puerto 8501, source `0.0.0.0/0`.

## 3. Conectarte e instalar Docker

```bash
ssh -i tu_llave.pem ubuntu@<IP_PUBLICA>
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

## 4. Subir el proyecto

```bash
git clone https://github.com/tu-usuario/mercado-central-agente.git
cd mercado-central-agente
```

## 5. Configurar la API key de Cohere

**Nunca subas tu API key al repositorio.** Créala en
https://dashboard.cohere.com/api-keys (gratis) y expórtala como variable
de entorno en la VM:

```bash
export COHERE_API_KEY="tu_api_key_aqui"
```

Para que persista entre reinicios de la VM, agrégala a `~/.bashrc`:
```bash
echo 'export COHERE_API_KEY="tu_api_key_aqui"' >> ~/.bashrc
```

(Opcional, más "cloud-native": guardar la key en **OCI Vault** en vez de
una variable de entorno plana, y leerla desde ahí en el arranque.)

## 6. Construir el índice (una sola vez, o cuando cambien los documentos)

```bash
docker compose run --rm app python src/ingest.py
docker compose run --rm app python src/embed_index.py
```

## 7. Levantar la app

```bash
docker compose up -d --build
```

## 8. Verificar

Abre `http://<IP_PUBLICA>:8501` en el navegador. Toma captura o graba un
video corto como evidencia de deploy para el README.

## 9. Registro de ejecución

Los logs quedan en `logs/agent_log.jsonl` (montado como volumen, persiste
en la VM):
```bash
docker exec -it mercado-central-agente cat logs/agent_log.jsonl
```

## Nota sobre costos

La API de Cohere tiene un **free tier** con límite de llamadas por minuto,
suficiente para un proyecto de demo/portafolio. Revisa los límites actuales
en https://dashboard.cohere.com — si los superas, no te cobra automático,
simplemente rechaza la llamada hasta que pueda de nuevo.

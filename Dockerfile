# Base image
FROM python:3.10-slim

# Diretório de trabalho
WORKDIR /app

# Instala dependências compiladas (caso o matplotlib precise)
RUN apt-get update && \
apt-get install -y --no-install-recommends \
build-essential \
libjpeg-dev \
zlib1g-dev && \
rm -rf /var/lib/apt/lists/*

# Copia e instala dependências via pip
COPY requirements.txt .
RUN pip install --upgrade pip && \
pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto para /app
COPY . .

# Evita buffers em logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Expõe a porta usada pelo Uvicorn
EXPOSE 5005

# Comando padrão para rodar o servidor FastAPI
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5005", "--lifespan=on", "--log-level", "info"]

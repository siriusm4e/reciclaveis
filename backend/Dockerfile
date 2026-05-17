# =============================================================================
# Backend FastAPI — Python 3.12 slim
# =============================================================================
# Inclui:
#   - libmagic1 (python-magic, validação MIME real de uploads)
#   - libpq-dev / gcc (build de asyncpg)
#   - curl (healthcheck)
# =============================================================================

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=America/Sao_Paulo

WORKDIR /app

# Dependências de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libmagic1 \
    curl \
    tzdata \
 && rm -rf /var/lib/apt/lists/*

# Dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Código (montado por volume em dev; copiado para build de prod)
COPY . .

# Garante storage subpastas
RUN mkdir -p storage/documentos storage/anuncios storage/avatares storage/conteudo

EXPOSE 8000

# Default = API. Worker e beat sobrescrevem `command` no docker-compose.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

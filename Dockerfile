# ═══════════════════════════════════════════════════════════════════════════════
# Empleo Tecnológico — MVP académico v0.2
# Imagen Docker reproducible para Streamlit + Jupyter
# ═══════════════════════════════════════════════════════════════════════════════

FROM python:3.11-slim AS base

LABEL org.opencontainers.image.authors="jtamames@unie.es"
LABEL org.opencontainers.image.title="Empleo TIC MVP"
LABEL org.opencontainers.image.description="Análisis crítico del empleo tecnológico EPA T1 2026"
LABEL org.opencontainers.image.source="https://github.com/jtamames/empleo-tic-mvp"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.version="0.2.0"

# Variables de entorno reproducibles
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    LANG=es_ES.UTF-8 \
    LC_ALL=C.UTF-8

# Sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias en capa separada para cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY . .

# Crear usuario no-root (buena práctica académica)
RUN groupadd -r unie && useradd -r -g unie -d /app unie && chown -R unie:unie /app
USER unie

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

EXPOSE 8501

# Streamlit por defecto. Para Jupyter usar:
#   docker run --entrypoint jupyter empleo-tic-mvp lab --ip 0.0.0.0 --port 8888 --no-browser --allow-root
ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0", \
            "--server.headless=true", \
            "--browser.gatherUsageStats=false"]

# FastAPI core image (deploy target: Render, matching the house pattern).
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# System deps kept minimal; add build-essential here if you enable [chem] (rdkit).
COPY pyproject.toml README.md ./
COPY vayu ./vayu
RUN pip install --upgrade pip && pip install -e ".[ai]"

EXPOSE 8000
CMD ["uvicorn", "vayu.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

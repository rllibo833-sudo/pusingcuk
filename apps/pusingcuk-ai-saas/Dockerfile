FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PUSINGCUK_SAAS_BIND=0.0.0.0
WORKDIR /app
COPY . /app
EXPOSE 8088
CMD ["sh", "-c", "export PUSINGCUK_SAAS_PORT=${PORT:-8088}; exec python apps/pusingcuk-ai-saas/server.py"]

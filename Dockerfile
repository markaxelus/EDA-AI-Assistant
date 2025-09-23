FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

RUN groupadd -r eda && useradd -r -g eda -d /app -s /bin/bash eda
RUN chown -R eda:eda /app
USER eda

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "-m", "src.ai_logs.main"]
CMD ["--help"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import src.ai_logs.main; print('OK')" || exit 1
FROM python:3.8-slim as builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc libpq-dev

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# INSTALL APPLICATION
COPY setup.py .
COPY README.md .
COPY ./order_api /app/order_api
COPY ./docs /app/docs
COPY setup.py /app
COPY /tests /app/tests
COPY README.md /app

RUN pip install --no-cache-dir -e .

COPY . .

# final stage
FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc libpq-dev

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/ .

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 3090

CMD ["gunicorn", "--bind=0.0.0.0:3090", "--workers=3", "--worker-class=uvicorn.workers.UvicornWorker", "--timeout=174000", "app:start_application()"]
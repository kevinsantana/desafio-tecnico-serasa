FROM python:3.8-slim as builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc libpq-dev

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY setup.py .
COPY README.md .
COPY ./user_api /app/user_api
COPY ./user_api/docs /app/user_api/docs
COPY setup.py /app
COPY /tests /app/tests
COPY README.md /app

RUN pip install --no-cache-dir -e .

COPY . .

# final stage
FROM python:3.8-slim

# ENVS
ENV SECRET_KEY=$SECRET_KEY

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc libpq-dev

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/ .

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 4090

CMD ["gunicorn", "--bind=0.0.0.0:4090", "--workers=3", "--worker-class=uvicorn.workers.UvicornWorker", "--timeout=174000", "app:start_application()"]
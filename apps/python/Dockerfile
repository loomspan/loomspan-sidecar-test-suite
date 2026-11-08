FROM python:3.13-slim@sha256:8d9d0b8bcf6506481eae4907c18f5e3e7902e629f5f6d684f9e7c32e85e3ddf0
WORKDIR /app
COPY requirements.lock .
COPY runtime-artifacts/python-sdk/*.whl /sdk/
RUN set -- /sdk/*.whl; test "$#" -eq 1 && \
    pip install --no-cache-dir -r requirements.lock "${1}[fastapi]" && pip check
COPY apps /app/apps
COPY fixtures /app/fixtures
CMD ["uvicorn", "apps.python.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]

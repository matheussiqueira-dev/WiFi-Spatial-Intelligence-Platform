FROM python:3.12-slim
WORKDIR /workspace
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY apps/api/requirements.runtime.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home spatial \
    && mkdir /workspace/runtime && chown spatial:spatial /workspace/runtime
COPY apps/api /workspace/apps/api
USER spatial
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:create_app", "--factory", "--app-dir", "apps/api", "--host", "0.0.0.0", "--port", "8000", "--ws-max-size", "4096", "--ws-max-queue", "16", "--no-proxy-headers"]

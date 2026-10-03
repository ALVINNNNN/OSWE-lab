FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home learner
COPY app.py .
COPY labs ./labs
COPY templates ./templates
COPY static ./static
USER 10001:10001
EXPOSE 8000
# One worker is intentional: each target keeps per-instance state in memory.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--worker-tmp-dir", "/tmp", "--access-logfile", "-", "app:create_app()"]

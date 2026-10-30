FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY field_vision/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY field_vision/*.py /app/field_vision/
RUN useradd --uid 10001 --create-home vision && chown -R vision:vision /app
USER vision
EXPOSE 8080
CMD ["uvicorn", "field_vision.serve:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--limit-concurrency", "8"]

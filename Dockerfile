FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000 \
    KERAS_HOME=/tmp/.keras MPLCONFIGDIR=/tmp/matplotlib TF_CPP_MIN_LOG_LEVEL=2

# Hugging Face Spaces runs containers as user 1000
RUN useradd -m -u 1000 user
WORKDIR /app
COPY requirements.txt requirements-ml.txt ./
RUN pip install --no-cache-dir -r requirements-ml.txt

COPY --chown=user:user . .
RUN chown user:user /app
USER user
RUN python -m ml.train_crop && python -m ml.train_yield && DJANGO_DEBUG=0 python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_knowledge && gunicorn agri_assistant.wsgi --bind 0.0.0.0:${PORT} --timeout 60 --workers 2 --threads 4"]

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SECRET_KEY=build-time-only \
    DJANGO_DEBUG=false

WORKDIR /app

COPY django_site/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY django_site/ .
RUN python manage.py collectstatic --noinput

COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]

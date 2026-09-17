FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

# ARG obligatorios: reflex export importa rxconfig.py (DATABASE_URL, API_URL) y
# los módulos de auth (JWT_SECRET_KEY, GOOGLE_*) al compilar el frontend.
# Se pasan desde docker-compose build.args (o --build-arg a mano).
ARG API_URL
ARG PUBLIC_URL
ARG DATABASE_URL
ARG JWT_SECRET_KEY
ARG ALLOWED_EMAIL_DOMAIN
ARG GOOGLE_CLIENT_ID
ARG GOOGLE_CLIENT_SECRET
ARG GOOGLE_REDIRECT_URI

ENV API_URL=$API_URL \
    PUBLIC_URL=$PUBLIC_URL \
    DATABASE_URL=$DATABASE_URL \
    JWT_SECRET_KEY=$JWT_SECRET_KEY \
    ALLOWED_EMAIL_DOMAIN=$ALLOWED_EMAIL_DOMAIN \
    GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID \
    GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET \
    GOOGLE_REDIRECT_URI=$GOOGLE_REDIRECT_URI

RUN apt-get update && apt-get install -y --no-install-recommends curl unzip postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Genera .web/ (skeleton) y compila el frontend. Sin estos pasos no habría
# frontend servido por el backend en modo prod.
RUN reflex init
RUN reflex export --frontend-only --no-zip

# En prod replax run --env prod expone TODO por el backend (frontend + API).
EXPOSE 8000
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
FROM python:3:12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHEDIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl unzip \ && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 3000 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD [ "/entrypoint.sh" ]
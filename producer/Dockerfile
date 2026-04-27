FROM python:3.10-slim
WORKDIR /app

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*
RUN pip install kafka-python requests

COPY producer.py .
COPY crontab /etc/cron.d/producer-cron

RUN chmod 0644 /etc/cron.d/producer-cron \
    && crontab /etc/cron.d/producer-cron

RUN touch /var/log/cron.log
CMD ["sh", "-lc", "cron -f"]

FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . /app

# Install cron
RUN apt-get update && apt-get install -y cron

# Create a cron job file
COPY cronjob /etc/cron.d/

CMD ["cron", "-f"]
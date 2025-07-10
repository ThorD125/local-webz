FROM python:3.12

# Install cron and required packages
RUN apt-get update && apt-get install -y cron

# Copy requirements and install Python packages
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy source code
WORKDIR /app
COPY . /app

# Install crontab and start cron
RUN crontab /app/crontab
CMD ["cron", "-f"]

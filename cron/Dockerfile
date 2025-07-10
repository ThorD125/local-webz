FROM python:3.12

# Install cron
RUN apt-get update && apt-get install -y cron

# Install Python packages
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy app files
WORKDIR /app
COPY . /app

# Install crontab and keep cron running
RUN crontab crontab
CMD ["cron", "-f"]

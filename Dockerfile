FROM python:3.11-slim

# Metadata
LABEL maintainer="achim"
LABEL description="Medibot - Multi-Doctor Doctolib Appointment Notifier"
LABEL version="1.0"

# Arbeitsverzeichnis erstellen
WORKDIR /app

# System-Dependencies installieren (falls nötig)
RUN apt-get update && apt-get install -y \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Timezone setzen (passe an deine Zone an)
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Python Dependencies (falls du welche hinzufügst)
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# App-Dateien kopieren
COPY medibot.py .
COPY config.py* ./

# Log-Verzeichnis erstellen
RUN mkdir -p /app/logs

# Non-root User erstellen (Sicherheit)
RUN useradd -m -u 1000 medibot && \
    chown -R medibot:medibot /app
USER medibot

# Health Check
HEALTHCHECK --interval=5m --timeout=10s --start-period=30s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('https://api.telegram.org')" || exit 1

# Default command (wird von docker-compose überschrieben)
CMD ["python3", "medibot.py"]

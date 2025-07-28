# 🐳 Docker Deployment Guide

Medibot kann einfach als Docker Container auf deinem vServer deployed werden.

## 🚀 Schnelle Installation

### Ein-Kommando Installation:
```bash
# Lade und führe das Deployment-Script aus
curl -sSL https://raw.githubusercontent.com/achimbarczok/medibot/main/deploy.sh | sudo bash

# Oder manuell:
wget https://raw.githubusercontent.com/achimbarczok/medibot/main/deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh
```

Das Script installiert automatisch:
- ✅ Docker & Docker Compose
- ✅ Klont das Repository nach `/opt/medibot`
- ✅ Erstellt Konfiguration aus Template
- ✅ Baut und startet Container
- ✅ Richtet Health-Monitoring ein
- ✅ Erstellt Management-Commands

## ⚙️ Zwei Deployment-Modi

### 1. Simple Mode (empfohlen für kleine vServer)
- Container startet, führt Script aus, beendet sich
- Host-Cron startet Container alle 10 Minuten
- Geringerer Speicherverbrauch

### 2. Cron Mode (empfohlen für größere Server)
- Container läuft dauerhaft
- Interner Cron führt Script alle 10 Minuten aus
- Etwas höherer Speicherverbrauch, aber stabiler

## 🛠️ Management Commands

Nach der Installation stehen dir diese Commands zur Verfügung:

```bash
medibot start        # Container starten
medibot stop         # Container stoppen
medibot restart      # Container neustarten
medibot logs         # Logs anzeigen (live)
medibot status       # Status und Container-Info
medibot update       # Update von GitHub
medibot config       # Konfiguration bearbeiten
medibot test         # Manueller Test-Lauf
medibot switch-mode  # Zwischen Modi wechseln
```

## 📝 Konfiguration

### 1. Nach Installation konfigurieren:
```bash
medibot config
```

### 2. Beispiel-Konfiguration:
```python
# Telegram Bot
TELEGRAM_BOT_TOKEN = '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'
TELEGRAM_CHAT_ID = '-123456789'

# Ärzte
DOCTORS = [
    {
        'name': 'Dr. Müller (Hausarzt)',
        'booking_url': 'https://www.doctolib.de/hausarzt/berlin/dr-mueller',
        'availabilities_url': 'https://www.doctolib.de/availabilities.json?visit_motive_ids=123456&agenda_ids=789&practice_ids=456&insurance_sector=public&limit=5',
        'move_booking_url': None
    }
]
```

### 3. Container neustarten:
```bash
medibot restart
```

## 📊 Monitoring

### Logs checken:
```bash
# Live Logs
medibot logs

# Spezifische Log-Dateien
tail -f /opt/medibot/logs/medibot.log
tail -f /opt/medibot/logs/cron.log        # Nur Cron-Mode
tail -f /opt/medibot/logs/host-cron.log   # Nur Simple-Mode
```

### Container Status:
```bash
medibot status
```

### Health-Check:
Das System prüft automatisch alle 5 Minuten ob Container laufen und startet sie bei Bedarf neu.

## 🔧 Manuelle Installation

Falls du das Deployment-Script nicht verwenden möchtest:

### 1. Repository klonen:
```bash
git clone https://github.com/achimbarczok/medibot.git /opt/medibot
cd /opt/medibot
```

### 2. Konfiguration erstellen:
```bash
cp config.py.template config.py
nano config.py
```

### 3. Container bauen und starten:
```bash
# Simple Mode
docker-compose up -d

# Oder Cron Mode  
docker-compose -f docker-compose.cron.yml up -d
```

## 🐛 Troubleshooting

### Container startet nicht:
```bash
docker-compose logs
docker-compose ps
```

### Konfigurationsfehler:
```bash
medibot test  # Testet Konfiguration
medibot config  # Konfiguration bearbeiten
```

### Permissions-Probleme:
```bash
sudo chown -R 1000:1000 /opt/medibot/logs
sudo chmod 755 /opt/medibot/logs
```

### Update-Probleme:
```bash
cd /opt/medibot
git pull origin main
docker-compose build
medibot restart
```

## 🔒 Sicherheit

### Non-Root Container:
- Container läuft als User `medibot` (UID 1000)
- Keine Root-Privileges im Container

### Ressourcen-Limits:
- Memory: 128MB Limit, 64MB Reservation
- CPU: 0.25 Cores Limit, 0.1 Cores Reservation

### Log-Rotation:
- Docker Logs: Max 10MB, 3 Dateien
- Automatische Rotation

## 📊 Monitoring erweitern

### Prometheus Monitoring (optional):
```bash
# Mit Monitoring-Profil starten
docker-compose --profile monitoring up -d

# Prometheus UI: http://your-server:9090
```

### Custom Health-Checks:
Das System überwacht automatisch:
- Container-Status
- Telegram API Erreichbarkeit
- Log-Dateien auf Fehler

## 🚀 Produktions-Empfehlungen

### 1. Backup-Strategie:
```bash
# Backup der Konfiguration
cp /opt/medibot/config.py ~/medibot-config-backup.py

# Backup der Logs
tar -czf ~/medibot-logs-$(date +%Y%m%d).tar.gz /opt/medibot/logs/
```

### 2. Updates:
```bash
# Automatische Updates (mit Vorsicht!)
echo "0 3 * * * cd /opt/medibot && git pull && docker-compose build && docker-compose up -d" | crontab -
```

### 3. Monitoring:
- Überwache `/opt/medibot/logs/` auf Disk-Usage
- Prüfe regelmäßig `medibot status`
- Teste Telegram-Bot monatlich

---

**🎉 Happy Deployment!** Bei Problemen siehe [README.md](README.md) oder erstelle ein GitHub Issue.

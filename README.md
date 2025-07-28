# Medibot 🤖

**Multi-Arzt Doctolib Termin-Benachrichtigungsbot für Telegram**

Automatische Überwachung von Doctolib-Arztterminen mit sofortigen Telegram-Benachrichtigungen bei verfügbaren Terminen.

![Python](https://img.shields.io/badge/python-v3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🔍 **Multi-Arzt Support**: Überwacht mehrere Ärzte gleichzeitig
- 📱 **Telegram-Benachrichtigungen**: Sofortige Push-Nachrichten auf dein Handy
- 🖥️ **Server-optimiert**: Läuft stabil via Cronjob auf Linux-Servern
- 📊 **Detaillierte Logs**: Vollständige Protokollierung aller Aktivitäten
- ⚡ **Rate-Limiting**: Schont Server mit konfigurierbaren Pausen
- 🛡️ **Fehlerbehandlung**: Robuste Behandlung von Netzwerk- und API-Fehlern

## 🚀 Quick Start

### 1. Repository klonen

```bash
git clone https://github.com/DEIN-USERNAME/medibot.git
cd medibot
```

### 2. Telegram Bot einrichten

1. **Bot erstellen**:
   - Starte Chat mit [@BotFather](https://t.me/botfather)
   - Sende `/newbot` und folge den Anweisungen
   - Speichere den **Bot Token**

2. **Telegram-Gruppe erstellen**:
   - Erstelle private Telegram-Gruppe
   - Füge Bot zur Gruppe hinzu (temporär "Allow Groups" aktivieren)
   - Sende Testnachricht mit `/test`

3. **Chat-ID ermitteln**:
   - Besuche: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Suche nach `"chat":{"id":-XXXXXXX}`
   - Kopiere die negative Zahl

### 3. Doctolib URLs sammeln

Für jeden Arzt den du überwachen willst:

1. Gehe zu [doctolib.de](https://www.doctolib.de/) und suche den Arzt
2. Klicke "Termin buchen"
3. Öffne Browser Developer Tools (F12) → Network Tab
4. Starte Terminbuchung aber **buche nicht wirklich**
5. Kopiere Browser-URL → `booking_url`
6. Finde `availabilities.json` Request → kopiere Request-URL → `availabilities_url`

### 4. Konfiguration

Bearbeite `medibot.py` und trage deine Daten ein:

```python
# Telegram Konfiguration
TELEGRAM_BOT_TOKEN = 'dein_bot_token_hier'
TELEGRAM_CHAT_ID = 'deine_chat_id_hier'  # negative Zahl!

# Ärzte hinzufügen
DOCTORS = [
    {
        'name': 'Dr. Müller (Hausarzt)',
        'booking_url': 'https://www.doctolib.de/hausarzt/berlin/dr-mueller',
        'availabilities_url': 'https://www.doctolib.de/availabilities.json?visit_motive_ids=123456&agenda_ids=789&practice_ids=456&insurance_sector=public&limit=5',
        'move_booking_url': None  # Optional: Termin verschieben URL
    },
    # Weitere Ärzte...
]
```

### 5. Testen

```bash
python3 medibot.py
```

### 6. Cronjob einrichten

```bash
crontab -e
```

Füge hinzu (Beispiel: alle 10 Minuten):
```bash
*/10 * * * * /usr/bin/python3 /pfad/zu/medibot/medibot.py
```

## ⚙️ Konfiguration

### Telegram Settings
- `TELEGRAM_BOT_TOKEN`: Bot Token von @BotFather
- `TELEGRAM_CHAT_ID`: Chat-ID deiner privaten Gruppe (negativ!)

### Ärzte-Konfiguration
Jeder Arzt in der `DOCTORS` Liste braucht:
- `name`: Anzeigename (optional)
- `booking_url`: Doctolib Buchungsseite
- `availabilities_url`: API URL aus Browser Dev Tools (**wichtig!**)
- `move_booking_url`: Termin verschieben URL (optional)

### Zeiteinstellungen
- `UPCOMING_DAYS`: Tage vorausschauen (max 15, Doctolib Limit)
- `NOTIFY_HOURLY`: Auch Updates für spätere Termine (false empfohlen)
- `REQUEST_DELAY`: Sekunden zwischen Arzt-Anfragen (3 empfohlen)
- `TIMEOUT`: HTTP Timeout (30 Sekunden)

## 📊 Monitoring

### Logs anschauen
```bash
tail -f medibot.log
```

### Letzten Durchlauf prüfen
```bash
grep "Medibot erfolgreich beendet" medibot.log | tail -1
```

### Erfolgreiche Benachrichtigungen zählen
```bash
grep "erfolgreich gesendet" medibot.log | wc -l
```

## 🕐 Cronjob Beispiele

```bash
# Alle 10 Minuten (empfohlen)
*/10 * * * * /usr/bin/python3 /opt/medibot/medibot.py

# Alle 5 Minuten (aggressiv)
*/5 * * * * /usr/bin/python3 /opt/medibot/medibot.py

# Nur tagsüber (7-22 Uhr)
*/10 7-22 * * * /usr/bin/python3 /opt/medibot/medibot.py

# Nur werktags (Mo-Fr, 8-18 Uhr)
*/15 8-18 * * 1-5 /usr/bin/python3 /opt/medibot/medibot.py
```

## ⚠️ Wichtige Hinweise

### Rechtlich
- **Nutzung auf eigenes Risiko** - könnte gegen Doctolib AGB verstoßen
- Script greift nur auf öffentlich verfügbare Daten zu
- Keine Garantie für dauerhaftes Funktionieren

### Ethisch
- Verwende das Script **sparsam** (nicht zu häufige Anfragen)
- Server-Ressourcen schonen mit angemessenen Pausen
- Bei Problemen Script sofort stoppen

### Technisch
- Doctolib kann URLs/API jederzeit ändern
- `availabilities_url` ist das Herzstück - muss regelmäßig aktualisiert werden
- Bei 403/429 Fehlern: längere Pausen einbauen

## 🛠️ Troubleshooting

### "❌ Telegram-Konfiguration fehlt!"
- Bot Token und Chat-ID korrekt eingetragen?
- Chat-ID muss negative Zahl sein (mit `-`)

### "❌ HTTP Fehler 403"
- Availabilities URL ist abgelaufen
- Neue URL über Browser Dev Tools ermitteln
- User-Agent im Code eventuell anpassen

### Keine Benachrichtigungen
- Script läuft ohne Fehler aber findet keine Termine → Normal!
- Teste mit einem Arzt der verfügbare Termine hat
- Prüfe Log-Ausgabe auf Fehler

### Bot antwortet nicht
- Bot Token korrekt?
- Bot zur Gruppe hinzugefügt?
- "Allow Groups" nach Hinzufügung wieder deaktiviert?

## 📈 Statistiken

Das Script protokolliert automatisch:
- Anzahl geprüfter Ärzte pro Durchlauf
- Gefundene Termine pro Arzt
- Gesendete Benachrichtigungen
- Fehler und deren Ursachen

## 🤝 Contributing

1. Fork das Repository
2. Erstelle Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📄 Lizenz

Dieses Projekt steht unter der MIT Lizenz - siehe [LICENSE.md](LICENSE.md) für Details.

## 🙏 Credits

**Original:** Basiert auf dem [Der Bergdoktorbot](https://github.com/mayrs/der-bergdoktorbot-a-doctolib-doctors-appointment-telegram-notifier) von [mayrs](https://github.com/mayrs).

**Entwicklung:** Erweitert um Multi-Arzt Support, Logging und Server-Optimierungen mit Unterstützung von [Claude (Anthropic)](https://claude.ai).

**Transparenz:** Dieses Projekt wurde unter Verwendung von KI-Assistenz entwickelt. Der Code wurde gemeinsam mit Claude erstellt, überprüft und optimiert, um eine robuste und benutzerfreundliche Lösung zu gewährleisten.

---

**⚠️ Disclaimer**: Dieses Tool ist für Bildungszwecke gedacht. Die Nutzung erfolgt auf eigenes Risiko. Der Autor übernimmt keine Haftung für Schäden oder Verstöße gegen Nutzungsbedingungen.

# =============================================================================
# KONFIGURATIONSBEISPIEL für medibot.py
# Kopiere diese Werte in dein medibot.py und passe sie an
# =============================================================================

# 🤖 TELEGRAM KONFIGURATION
TELEGRAM_BOT_TOKEN = '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'  # Von @BotFather
TELEGRAM_CHAT_ID = '-123456789'  # Deine Chat-ID (MUSS negativ sein!)

# 👨‍⚕️ ÄRZTE KONFIGURATION
DOCTORS = [
    {
        'name': 'Dr. Müller (Hausarzt)',
        'booking_url': 'https://www.doctolib.de/allgemeinmedizin/berlin/dr-mueller',
        'availabilities_url': 'https://www.doctolib.de/availabilities.json?visit_motive_ids=123456&agenda_ids=456789&practice_ids=789012&insurance_sector=public&limit=5',
        'move_booking_url': None
    },
    {
        'name': 'Dr. Schmidt (Orthopäde)', 
        'booking_url': 'https://www.doctolib.de/orthopade/berlin/dr-schmidt',
        'availabilities_url': 'https://www.doctolib.de/availabilities.json?visit_motive_ids=654321&agenda_ids=987654&practice_ids=345678&insurance_sector=public&limit=5',
        'move_booking_url': None
    }
]

# ⚙️ EINSTELLUNGEN
UPCOMING_DAYS = 15        # Tage vorausschauen (max 15)
NOTIFY_HOURLY = False     # Stündliche Updates für spätere Termine
REQUEST_DELAY = 3         # Sekunden zwischen Arzt-Anfragen
TIMEOUT = 30             # HTTP Timeout

# =============================================================================
# 📋 ANLEITUNG: WIE BEKOMME ICH DIE URLs?
# =============================================================================

"""
SCHRITT 1: TELEGRAM BOT ERSTELLEN
================================
1. Chatte mit @BotFather auf Telegram
2. Sende: /newbot
3. Wähle Name und Username (muss auf 'bot' enden)
4. Kopiere den Bot Token

SCHRITT 2: TELEGRAM GRUPPE ERSTELLEN
===================================
1. Erstelle private Telegram-Gruppe
2. Aktiviere temporär "Allow Groups" beim Bot
3. Füge Bot zur Gruppe hinzu  
4. Deaktiviere "Allow Groups" wieder
5. Sende Nachricht mit /test

SCHRITT 3: CHAT-ID ERMITTELN
===========================
1. Besuche: https://api.telegram.org/bot<DEIN_TOKEN>/getUpdates
2. Suche nach: "chat":{"id":-XXXXXXX
3. Kopiere die negative Zahl (mit dem Minus!)

SCHRITT 4: DOCTOLIB URLs SAMMELN
================================
Für jeden Arzt:

1. Gehe zu doctolib.de
2. Suche nach dem Arzt
3. Klicke "Termin buchen"
4. Öffne Browser Developer Tools (F12)
5. Gehe zum "Network" Tab
6. Aktiviere Filter "Fetch/XHR"
7. Starte Terminbuchung (aber buche NICHT wirklich!)
8. Kopiere Browser-URL → das ist die booking_url
9. Suche nach "availabilities.json" Request
10. Kopiere die komplette Request-URL → das ist die availabilities_url

WICHTIG: Die availabilities_url ist das Herzstück!
Sie enthält alle wichtigen Parameter und sieht etwa so aus:
https://www.doctolib.de/availabilities.json?visit_motive_ids=123456&agenda_ids=456789&practice_ids=789012&insurance_sector=public&limit=5

ALLE Parameter sind wichtig - kopiere die komplette URL!
"""

# =============================================================================
# 🚀 TESTEN
# =============================================================================

"""
1. Werte oben in medibot.py eintragen
2. Ausführen: python3 medibot.py
3. Logs prüfen in medibot.log
4. Bei Erfolg: Cronjob einrichten

CRONJOB BEISPIEL (alle 10 Minuten):
*/10 * * * * /usr/bin/python3 /pfad/zu/medibot.py
"""

#!/usr/bin/env python3
"""
Medibot - Doctolib Appointment Notifier
Multi-Arzt Version für Server/Cronjob Betrieb

Basiert auf: https://github.com/mayrs/der-bergdoktorbot-a-doctolib-doctors-appointment-telegram-notifier
Erweitert um: Multi-Arzt Support, Logging, Server-Optimierungen
"""

from datetime import date, datetime, timedelta
import json
import urllib.parse
import urllib.request
import logging
import sys
import time
from pathlib import Path

# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging():
    """Konfiguriert Logging für Server-Betrieb"""
    script_dir = Path(__file__).parent
    log_file = script_dir / 'medibot.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# =============================================================================
# KONFIGURATION LADEN
# =============================================================================

def load_config():
    """Lädt Konfiguration aus config.py oder verwendet Defaults"""
    
    # Standard-Konfiguration
    config = {
        'TELEGRAM_BOT_TOKEN': '',
        'TELEGRAM_CHAT_ID': '',
        'DOCTORS': [],
        'UPCOMING_DAYS': 15,
        'NOTIFY_HOURLY': False,
        'REQUEST_DELAY': 3,
        'TIMEOUT': 30
    }
    
    # Versuche config.py zu importieren
    try:
        import config
        
        # Lade Werte aus config.py
        for key in config.keys():
            if hasattr(config_module := config, key):
                config[key] = getattr(config_module, key)
        
        logger.info("✅ Konfiguration aus config.py geladen")
        
    except ImportError:
        logger.info("ℹ️ Keine config.py gefunden - verwende Inline-Konfiguration")
        
        # =================================================================
        # INLINE KONFIGURATION - HIER DEINE DATEN EINTRAGEN
        # =================================================================
        
        # 🤖 TELEGRAM KONFIGURATION
        config['TELEGRAM_BOT_TOKEN'] = ''  # Dein Bot Token von @BotFather
        config['TELEGRAM_CHAT_ID'] = ''    # Deine Chat ID (negative Zahl)
        
        # 👨‍⚕️ ÄRZTE KONFIGURATION - Hier alle Ärzte eintragen
        config['DOCTORS'] = [
            {
                'name': 'Dr. Beispiel (Hausarzt)',
                'booking_url': 'https://www.doctolib.de/',
                'availabilities_url': '',  # Die availabilities.json URL aus Browser Dev Tools
                'move_booking_url': None   # Optional: Termin verschieben URL
            },
            # Weitere Ärzte hier hinzufügen:
            # {
            #     'name': 'Dr. Muster (Orthopäde)',
            #     'booking_url': 'https://www.doctolib.de/orthopade/berlin/dr-muster',
            #     'availabilities_url': 'https://www.doctolib.de/availabilities.json?visit_motive_ids=123456&agenda_ids=789&practice_ids=456&insurance_sector=public&limit=5',
            #     'move_booking_url': None
            # },
        ]
        
        # ⚙️ ERWEITERTE EINSTELLUNGEN
        config['UPCOMING_DAYS'] = 15        # Tage vorausschauen (max 15 wegen Doctolib Limit)
        config['NOTIFY_HOURLY'] = False     # Stündliche Updates auch für spätere Termine
        config['REQUEST_DELAY'] = 3         # Sekunden Pause zwischen Arzt-Anfragen
        config['TIMEOUT'] = 30             # HTTP Timeout in Sekunden
        
        # =================================================================
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Laden der Konfiguration: {e}")
        sys.exit(1)
    
    return config

# Globale Konfiguration laden
CONFIG = load_config()

# =============================================================================
# VALIDIERUNG
# =============================================================================

def validate_config():
    """Überprüft die Konfiguration"""
    
    if not CONFIG['TELEGRAM_BOT_TOKEN'] or not CONFIG['TELEGRAM_CHAT_ID']:
        logger.error("❌ Telegram-Konfiguration fehlt!")
        logger.error("💡 Trage TELEGRAM_BOT_TOKEN und TELEGRAM_CHAT_ID ein")
        logger.error("📖 Hilfe: Siehe config_example.py oder README.md")
        sys.exit(1)
    
    if not CONFIG['DOCTORS']:
        logger.error("❌ Keine Ärzte konfiguriert!")
        logger.error("💡 Füge mindestens einen Arzt zur DOCTORS Liste hinzu")
        logger.error("📖 Hilfe: Siehe config_example.py")
        sys.exit(1)
    
    if CONFIG['UPCOMING_DAYS'] > 15:
        logger.error("❌ UPCOMING_DAYS darf nicht größer als 15 sein (Doctolib Limit)")
        sys.exit(1)
    
    # Ärzte validieren
    valid_doctors = []
    for i, doctor in enumerate(CONFIG['DOCTORS']):
        if not doctor.get('availabilities_url'):
            logger.warning(f"⚠️ Arzt {i+1} ({doctor.get('name', 'Unbekannt')}) übersprungen - keine availabilities_url")
            continue
        
        # Default-Werte setzen
        if not doctor.get('name'):
            doctor['name'] = f"Arzt {i+1}"
        if not doctor.get('booking_url'):
            doctor['booking_url'] = 'https://www.doctolib.de/'
        
        valid_doctors.append(doctor)
    
    if not valid_doctors:
        logger.error("❌ Keine gültigen Ärzte konfiguriert!")
        logger.error("💡 Mindestens ein Arzt braucht eine 'availabilities_url'")
        sys.exit(1)
    
    # Validierte Ärzte-Liste aktualisieren
    CONFIG['DOCTORS'] = valid_doctors
    
    logger.info(f"✅ Konfiguration OK - {len(valid_doctors)} Ärzte konfiguriert")

# =============================================================================
# HAUPTLOGIK
# =============================================================================

def check_doctor_appointments(doctor):
    """Prüft Termine für einen einzelnen Arzt"""
    
    name = doctor.get('name', 'Unbekannter Arzt')
    logger.info(f"🔍 Prüfe {name}...")
    
    try:
        # URL Parameter für aktuelles Datum anpassen
        urlParts = urllib.parse.urlparse(doctor['availabilities_url'])
        query = dict(urllib.parse.parse_qsl(urlParts.query))
        query.update({
            'limit': CONFIG['UPCOMING_DAYS'],
            'start_date': date.today().isoformat(),
        })
        
        newAvailabilitiesUrl = (urlParts
                               ._replace(query=urllib.parse.urlencode(query))
                               .geturl())
        
        # HTTP Request mit Headers
        request = urllib.request.Request(newAvailabilitiesUrl)
        request.add_header(
            'User-Agent',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        # Request senden
        response = urllib.request.urlopen(request, timeout=CONFIG['TIMEOUT'])
        availabilities = json.loads(response.read().decode('utf-8'))
        
        slotsInNearFuture = availabilities.get('total', 0)
        logger.info(f"  📊 {slotsInNearFuture} Termine in den nächsten {CONFIG['UPCOMING_DAYS']} Tagen")
        
        if slotsInNearFuture == 0:
            logger.info(f"  ℹ️ Keine Termine verfügbar für {name}")
            return False
        
        # Prüfe auf frühe Termine (innerhalb der Zeitgrenze)
        earlierSlotExists = False
        earliest_date = None
        max_datetime = datetime.today() + timedelta(days=CONFIG['UPCOMING_DAYS'])
        
        for day in availabilities.get('availabilities', []):
            if len(day.get('slots', [])) == 0:
                continue
            
            nextDatetimeIso8601 = day['date']
            nextDatetime = datetime.fromisoformat(nextDatetimeIso8601).replace(tzinfo=None)
            
            if nextDatetime < max_datetime:
                earlierSlotExists = True
                if not earliest_date or nextDatetime < earliest_date:
                    earliest_date = nextDatetime
                logger.info(f"  ✅ Früher Termin: {nextDatetime.strftime('%d.%m.%Y %H:%M')}")
                break
        
        # Entscheide ob Benachrichtigung gesendet werden soll
        isOnTheHour = datetime.now().minute == 0
        isHourlyNotificationDue = isOnTheHour and CONFIG['NOTIFY_HOURLY']
        
        if earlierSlotExists or isHourlyNotificationDue:
            send_notification(doctor, slotsInNearFuture, earlierSlotExists, earliest_date, availabilities)
            return True
        else:
            logger.info(f"  ℹ️ Keine frühen Termine für {name}")
            return False
    
    except urllib.error.HTTPError as e:
        logger.error(f"  ❌ HTTP Fehler bei {name}: {e.code} {e.reason}")
        return False
    except urllib.error.URLError as e:
        logger.error(f"  ❌ Verbindungsfehler bei {name}: {e.reason}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"  ❌ JSON Fehler bei {name}: {e}")
        return False
    except Exception as e:
        logger.error(f"  ❌ Unerwarteter Fehler bei {name}: {e}")
        return False

def send_notification(doctor, slot_count, early_slots, earliest_date, availabilities):
    """Sendet Telegram-Benachrichtigung für einen Arzt"""
    
    name = doctor.get('name', 'Arzt')
    
    # Nachricht zusammenbauen
    message = f'👨‍⚕️👩‍⚕️ {name}\n'
    
    if early_slots:
        plural = 's' if slot_count > 1 else ''
        message += f'🔥 {slot_count} Termin{plural} in den nächsten {CONFIG["UPCOMING_DAYS"]} Tagen!\n'
        
        if earliest_date:
            date_str = earliest_date.strftime('%d.%m.%Y um %H:%M')
            message += f'📅 Frühester Termin: {date_str}\n'
        
        if doctor.get('move_booking_url'):
            message += f'<a href="{doctor["move_booking_url"]}">🚚 Bestehenden Termin verschieben</a>\n'
    
    if CONFIG['NOTIFY_HOURLY'] and 'next_slot' in availabilities:
        nextSlotDatetimeIso8601 = availabilities['next_slot']
        nextSlotDate = datetime.fromisoformat(nextSlotDatetimeIso8601).strftime('%d.%m.%Y')
        message += f'🐌 Nächster verfügbarer Termin: {nextSlotDate}\n'
    
    message += f'📞 <a href="{doctor["booking_url"]}">Jetzt auf Doctolib buchen</a>'
    
    # Telegram-Nachricht senden
    success = send_telegram_message(message)
    if success:
        logger.info(f"  📱 Benachrichtigung für {name} erfolgreich gesendet")
    else:
        logger.error(f"  ❌ Benachrichtigung für {name} fehlgeschlagen")
    
    return success

def send_telegram_message(message):
    """Sendet eine Nachricht über die Telegram Bot API"""
    
    try:
        urlEncodedMessage = urllib.parse.quote(message)
        telegram_url = (
            f'https://api.telegram.org/bot{CONFIG["TELEGRAM_BOT_TOKEN"]}/sendMessage'
            f'?chat_id={CONFIG["TELEGRAM_CHAT_ID"]}'
            f'&text={urlEncodedMessage}'
            f'&parse_mode=HTML'
            f'&disable_web_page_preview=true'
        )
        
        urllib.request.urlopen(telegram_url, timeout=CONFIG['TIMEOUT'])
        return True
        
    except Exception as e:
        logger.error(f"Telegram API Fehler: {e}")
        return False

def send_summary_notification(total_doctors, notifications_sent):
    """Sendet Zusammenfassung wenn keine Termine gefunden wurden"""
    
    if notifications_sent == 0 and total_doctors >= 3:
        timestamp = datetime.now().strftime('%d.%m.%Y um %H:%M')
        message = (
            f"📋 Medibot Zusammenfassung\n"
            f"🔍 {total_doctors} Ärzte überprüft\n"
            f"😴 Keine neuen Termine gefunden\n"
            f"🕐 {timestamp}\n"
            f"⏰ Nächste Prüfung entsprechend Cronjob"
        )
        send_telegram_message(message)
        logger.info("📊 Zusammenfassungsbenachrichtigung gesendet")

def send_startup_error(error_msg):
    """Sendet Fehler-Benachrichtigung falls möglich"""
    
    if CONFIG.get('TELEGRAM_BOT_TOKEN') and CONFIG.get('TELEGRAM_CHAT_ID'):
        timestamp = datetime.now().strftime('%d.%m.%Y um %H:%M')
        message = (
            f"⚠️ Medibot Startup-Fehler\n"
            f"💥 {error_msg}\n"
            f"🕐 {timestamp}\n"
            f"🔧 Bitte Konfiguration prüfen"
        )
        send_telegram_message(message)

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Hauptfunktion - wird vom Cronjob aufgerufen"""
    
    logger.info("=" * 60)
    logger.info("🚀 Medibot gestartet")
    
    try:
        # Konfiguration validieren
        validate_config()
        
        doctors = CONFIG['DOCTORS']
        
        logger.info(f"📋 Starte Terminprüfung für {len(doctors)} Ärzte")
        logger.info(f"📅 Suche nach Terminen in den nächsten {CONFIG['UPCOMING_DAYS']} Tagen")
        
        notifications_sent = 0
        
        # Jeden Arzt einzeln prüfen
        for i, doctor in enumerate(doctors, 1):
            logger.info(f"\n[{i}/{len(doctors)}] Bearbeite Arzt...")
            
            if check_doctor_appointments(doctor):
                notifications_sent += 1
            
            # Pause zwischen Requests (außer beim letzten)
            if i < len(doctors) and CONFIG['REQUEST_DELAY'] > 0:
                logger.info(f"  ⏱️ Warte {CONFIG['REQUEST_DELAY']} Sekunden...")
                time.sleep(CONFIG['REQUEST_DELAY'])
        
        # Zusammenfassung
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ Terminprüfung abgeschlossen!")
        logger.info(f"📊 Ergebnis: {notifications_sent}/{len(doctors)} Benachrichtigungen gesendet")
        
        # Zusammenfassungsbenachrichtigung bei vielen Ärzten ohne Funde
        send_summary_notification(len(doctors), notifications_sent)
        
    except KeyboardInterrupt:
        logger.info("❌ Medibot durch Benutzer beendet (Ctrl+C)")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"💥 Unerwarteter Fehler: {e}")
        send_startup_error(f"Unerwarteter Fehler: {e}")
        sys.exit(1)
    
    logger.info("🏁 Medibot erfolgreich beendet")

if __name__ == "__main__":
    main()

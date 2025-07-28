#!/bin/bash
# Medibot Setup Helper

echo "🚀 Medibot Setup Helper"
echo "======================"

# Python Version prüfen
echo "🐍 Python Version:"
python3 --version || { echo "❌ Python3 nicht installiert!"; exit 1; }

# Aktuelles Verzeichnis prüfen
if [ ! -f "medibot.py" ]; then
    echo "❌ medibot.py nicht gefunden! Bist du im richtigen Verzeichnis?"
    exit 1
fi

echo "✅ medibot.py gefunden"

# Konfiguration prüfen
echo ""
echo "🔧 Konfiguration prüfen..."

# Prüfe ob separate config.py existiert
if [ -f "config.py" ]; then
    echo "✅ config.py gefunden - verwende separate Konfigurationsdatei"
    
    if grep -q "TELEGRAM_BOT_TOKEN = ''" config.py; then
        echo "⚠️  TELEGRAM_BOT_TOKEN ist leer in config.py!"
        CONFIG_MISSING=1
    fi
    
    if grep -q "TELEGRAM_CHAT_ID = ''" config.py; then
        echo "⚠️  TELEGRAM_CHAT_ID ist leer in config.py!"
        CONFIG_MISSING=1
    fi
    
else
    echo "ℹ️  Keine config.py gefunden - prüfe Inline-Konfiguration in medibot.py"
    
    if grep -q "config\['TELEGRAM_BOT_TOKEN'\] = ''" medibot.py; then
        echo "⚠️  TELEGRAM_BOT_TOKEN ist leer - bitte konfigurieren!"
        CONFIG_MISSING=1
    fi
    
    if grep -q "config\['TELEGRAM_CHAT_ID'\] = ''" medibot.py; then
        echo "⚠️  TELEGRAM_CHAT_ID ist leer - bitte konfigurieren!"
        CONFIG_MISSING=1
    fi
fi

if grep -q "availabilities_url': ''" medibot.py || ([ -f "config.py" ] && grep -q "availabilities_url': ''" config.py); then
    echo "⚠️  Mindestens ein Arzt hat keine availabilities_url!"
    CONFIG_MISSING=1
fi

if [ "$CONFIG_MISSING" ]; then
    echo ""
    echo "📝 Nächste Schritte:"
    echo "OPTION A: Separate Konfigurationsdatei (empfohlen)"
    echo "1. cp config.py.template config.py"
    echo "2. Bearbeite config.py mit deinen Daten"
    echo ""
    echo "OPTION B: Inline-Konfiguration"
    echo "1. Öffne medibot.py in einem Editor"
    echo "2. Suche nach 'INLINE KONFIGURATION'"
    echo "3. Trage deine Daten dort ein"
    echo ""
    echo "💡 Hilfe: Siehe config_example.py für Beispiele"
    exit 1
fi

echo "✅ Grundkonfiguration scheint vollständig"

# Test-Lauf
echo ""
echo "🧪 Test-Lauf starten..."
echo "Logs werden in medibot.log geschrieben"
echo ""

python3 medibot.py

# Ergebnis prüfen
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Test erfolgreich!"
    echo ""
    echo "📋 Nächste Schritte:"
    echo "1. Logs prüfen: tail -f medibot.log"
    echo "2. Cronjob einrichten: crontab -e"
    echo "3. Beispiel-Cronjob: */10 * * * * /usr/bin/python3 $(pwd)/medibot.py"
    echo ""
else
    echo ""
    echo "❌ Test fehlgeschlagen!"
    echo "📝 Prüfe die Logs: tail medibot.log"
    echo "🔧 Häufige Probleme:"
    echo "   - Falsche Telegram Token/Chat-ID"
    echo "   - Ungültige availabilities_url"  
    echo "   - Netzwerkprobleme"
fi

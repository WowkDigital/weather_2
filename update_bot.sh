#!/bin/bash

# Nazwa sesji screen
SESSION_NAME="weather_bot"
# Nazwa pliku głównego
BOT_FILE="main.py"

echo "------------------------------------------"
echo "🚀 Rozpoczynam aktualizację bota..."
echo "------------------------------------------"

# 1. Zatrzymanie bota (jeśli sesja istnieje)
if screen -list | grep -q "$SESSION_NAME"; then
    echo "🛑 Zatrzymuję pracującą sesję: $SESSION_NAME"
    screen -S "$SESSION_NAME" -X quit
    sleep 2
else
    echo "ℹ️ Bot nie był uruchomiony (brak aktywnej sesji screen)."
fi

# 2. Pobranie najnowszego kodu z Git
echo "📂 Pobieram najnowsze zmiany z Git (git pull)..."
git pull origin main

# 3. Instalacja ewentualnych nowych zależności
if [ -f "requirements.txt" ]; then
    echo "📦 Aktualizuję biblioteki z requirements.txt..."
    # Sprawdź czy istnieje venv, jeśli tak - użyj go
    if [ -d "venv" ]; then
        ./venv/bin/pip install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
fi

# 4. Ponowne uruchomienie bota w nowej sesji screen
echo "⏳ Uruchamiam bota w nowej sesji screen: $SESSION_NAME..."
if [ -d "venv" ]; then
    screen -dmS "$SESSION_NAME" bash -c "source venv/bin/activate && python3 $BOT_FILE"
else
    screen -dmS "$SESSION_NAME" python3 $BOT_FILE
fi

echo "------------------------------------------"
echo "✅ Aktualizacja zakończona sukcesem!"
echo "🔍 Aby podejrzeć bota, wpisz: screen -r $SESSION_NAME"
echo "------------------------------------------"

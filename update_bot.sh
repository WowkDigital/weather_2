#!/bin/bash

# Configuration
SESSION_NAME="weather_bot"
BOT_FILE="main.py"
START_TIME=$SECONDS

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "        🚀 AKTUALIZACJA WEATHER BOT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Stop Bot
if screen -list | grep -q "$SESSION_NAME"; then
    screen -S "$SESSION_NAME" -X quit > /dev/null 2>&1
    STATUS_STOP="✅ ZATRZYMANO"
else
    STATUS_STOP="ℹ️ NIE URUCHOMIONY"
fi

# 2. Git Pull
if git pull origin main > /dev/null 2>&1; then
    STATUS_GIT="✅ POBRANO"
else
    STATUS_GIT="❌ BŁĄD GIT"
fi

# 3. Dependencies
if [ -f "requirements.txt" ]; then
    VENV_PATH="./venv/bin/pip"
    [ ! -f "$VENV_PATH" ] && VENV_PATH="pip"
    
    if $VENV_PATH install -r requirements.txt > /dev/null 2>&1; then
        STATUS_DEPS="✅ ZAAKTUALIZOWANO"
    else
        STATUS_DEPS="❌ BŁĄD PIP"
    fi
else
    STATUS_DEPS="➖ BRAK REQ.TXT"
fi

# 4. Start Bot
if [ -d "venv" ]; then
    screen -dmS "$SESSION_NAME" bash -c "source venv/bin/activate && python3 $BOT_FILE"
else
    screen -dmS "$SESSION_NAME" python3 $BOT_FILE
fi
STATUS_START="✅ URUCHOMIONO"

# Calculation of time
ELAPSED_TIME=$(( SECONDS - START_TIME ))

echo " [1/4] Sesja screen:     $STATUS_STOP"
echo " [2/4] Kod (Git):        $STATUS_GIT"
echo " [3/4] Zależności:       $STATUS_DEPS"
echo " [4/4] Status bota:      $STATUS_START"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ✨ Wynik:  Pomyślnie zaktualizowano!"
echo " ⏳ Czas:   ${ELAPSED_TIME} sekund"
echo " 🔍 Podgląd: screen -r $SESSION_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

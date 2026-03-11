#!/bin/bash

# Configuration
SESSION_NAME="weather_bot"
BOT_FILE="main.py"
START_TIME=$SECONDS

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "        🚀 AKTUALIZACJA WEATHER BOT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Start: Anchor to script directory
cd "$(dirname "$0")"

# 1.1 Stop Bot
if screen -list | grep -q "$SESSION_NAME"; then
    screen -S "$SESSION_NAME" -X quit > /dev/null 2>&1
    STATUS_STOP="✅ ZATRZYMANO"
else
    STATUS_STOP="ℹ️ NIE URUCHOMIONY"
fi

# 2. Git Pull
PRE_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
GIT_OUT=$(git pull origin main 2>&1)
GIT_EXIT=$?

if [ $GIT_EXIT -eq 0 ]; then
    POST_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    COMMIT_MSG=$(git log -1 --format="%s" 2>/dev/null || echo "N/A")
    
    if [ "$PRE_COMMIT" != "$POST_COMMIT" ]; then
        STATUS_GIT="✅ POBRANO ($POST_COMMIT)"
        COMMIT_INFO="🆕 Nowy commit: $POST_COMMIT - $COMMIT_MSG"
    else
        STATUS_GIT="✅ AKTUALNY"
        COMMIT_INFO="ℹ️ Już aktualny: $POST_COMMIT - $COMMIT_MSG"
    fi
else
    STATUS_GIT="❌ BŁĄD GIT"
    COMMIT_INFO="⚠️ Błąd: $(echo "$GIT_OUT" | head -n 5 | tr '\n' ' ')"
fi


# 3. Dependencies
if [ -f "requirements.txt" ]; then
    # Ensure venv exists
    if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
        echo "⚠️ Nie znaleziono środowiska wirtualnego. Tworzę 'venv'..."
        python3 -m venv venv > /dev/null 2>&1
    fi

    # Detect pip path
    if [ -d "venv" ]; then
        PIP_PATH="./venv/bin/pip"
        PYTHON_PATH="./venv/bin/python3"
    elif [ -d ".venv" ]; then
        PIP_PATH="./.venv/bin/pip"
        PYTHON_PATH="./.venv/bin/python3"
    else
        # Fallback to system pip and hope for the best, but show warning
        PIP_PATH="pip3"
        PYTHON_PATH="python3"
        echo "⚠️ UWAGA: Używam systemowego pip3 (brak venv). Może wystąpić błąd PEP 668."
    fi

    echo "⏳ Instalowanie zależności z requirements.txt..."
    if $PIP_PATH install --upgrade -r requirements.txt > pip_error.log 2>&1; then
        STATUS_DEPS="✅ ZAAKTUALIZOWANO"
        rm -f pip_error.log
    else
        STATUS_DEPS="❌ BŁĄD PIP (sprawdź pip_error.log)"
        # Suggest fix for PEP 668 if visible in log
        if grep -q "externally-managed-environment" pip_error.log; then
             STATUS_DEPS="❌ BŁĄD (PEP 668 - spróbuj: python3 -m venv venv)"
        fi
    fi
else
    STATUS_DEPS="➖ BRAK REQ.TXT"
fi



# 4. Start Bot
LOG_FILE="bot.log"
if [ -d "venv" ]; then
    screen -dmS "$SESSION_NAME" bash -c "source venv/bin/activate && python3 $BOT_FILE > $LOG_FILE 2>&1"
elif [ -d ".venv" ]; then
    screen -dmS "$SESSION_NAME" bash -c "source .venv/bin/activate && python3 $BOT_FILE > $LOG_FILE 2>&1"
else
    screen -dmS "$SESSION_NAME" bash -c "python3 $BOT_FILE > $LOG_FILE 2>&1"
fi

# Wait a moment and check if still running
sleep 2
if screen -list | grep -q "$SESSION_NAME"; then
    STATUS_START="✅ URUCHOMIONO"
else
    STATUS_START="❌ CRASH (zobacz screen -r lub logi)"
fi


# Calculation of time
ELAPSED_TIME=$(( SECONDS - START_TIME ))

echo " [1/4] Zatrzymanie bota:  $STATUS_STOP"
echo " [2/4] Kod (Git):        $STATUS_GIT"
echo " [3/4] Zależności:       $STATUS_DEPS"
echo " [4/4] Start nowej sesji: $STATUS_START"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " $COMMIT_INFO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ✨ Wynik:  Pomyślnie zaktualizowano!"
echo " ⏳ Czas:   ${ELAPSED_TIME} sekund"
echo " 🔍 Podgląd: screen -r $SESSION_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

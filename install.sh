#!/bin/bash

# Configuration
SESSION_NAME="weather_bot"
BOT_FILE="main.py"
ENV_FILE=".env"
ENV_EXAMPLE=".env.example"

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "        🚀 INSTALACJA WEATHER BOT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Anchor to script directory
cd "$(dirname "$0")"

# 2. Check for system dependencies
echo "🔍 Sprawdzanie zależności systemowych..."
MISSING_DEPS=()
for cmd in python3 pip3 screen; do
    if ! command -v $cmd &> /dev/null; then
        MISSING_DEPS+=("$cmd")
    fi
done

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "⚠️  Brakujące pakiety: ${MISSING_DEPS[*]}"
    echo "💡 Spróbuj: sudo apt update && sudo apt install python3 python3-pip python3-venv screen -y"
    # Don't exit here, maybe the user can't sudo but has them in path.
fi

# 3. Create Virtual Environment
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "⏳ Tworzenie środowiska wirtualnego (venv)..."
    if python3 -m venv venv; then
        echo "✅ Środowisko venv utworzone."
        VENV_PATH="venv"
    else
        echo "❌ BŁĄD: Nie udało się utworzyć venv. Sprawdź czy masz zainstalowany python3-venv."
        exit 1
    fi
else
    echo "✅ Środowisko wirtualne już istnieje."
    [ -d "venv" ] && VENV_PATH="venv" || VENV_PATH=".venv"
fi

# 4. Install Dependencies
echo "⏳ Instalowanie zależności z requirements.txt..."
if $VENV_PATH/bin/pip install --upgrade -r requirements.txt; then
    echo "✅ Zależności zainstalowane pomyślnie."
else
    echo "❌ BŁĄD: Nie udało się zainstalować zależności. Sprawdź logi powyżej."
    exit 1
fi

# 5. Setup .env file
if [ ! -f "$ENV_FILE" ]; then
    echo "📄 Konfiguracja pliku .env..."
    if [ -f "$ENV_EXAMPLE" ]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        echo "✅ Skopiowano $ENV_EXAMPLE do $ENV_FILE."
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "⚠️  UWAGA: Musisz teraz uzupełnić klucze API w pliku .env"
        echo "Podaj TELEGRAM_BOT_TOKEN (lub naciśnij Enter, aby pominąć):"
        read -r bot_token
        if [ -n "$bot_token" ]; then
            sed -i "s|YOUR_TELEGRAM_BOT_TOKEN|$bot_token|" "$ENV_FILE"
        fi
        
        echo "Podaj WEATHER_API_KEY (lub naciśnij Enter, aby pominąć):"
        read -r api_key
        if [ -n "$api_key" ]; then
            sed -i "s|YOUR_WEATHER_API_KEY|$api_key|" "$ENV_FILE"
        fi
        echo "✅ Zaktualizowano $ENV_FILE."
    else
        echo "⚠️  UWAGA: Nie znaleziono $ENV_EXAMPLE. Utwórz plik .env ręcznie."
    fi
else
    echo "✅ Plik .env już istnieje."
fi

# 6. Final message
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ✨ Instalacja zakończona pomyślnie!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 🚀 Aby uruchomić bota teraz, wpisz:"
echo "    ./update_bot.sh"
echo ""
echo " 📈 Aby ręcznie uruchomić w screen:"
echo "    screen -dmS $SESSION_NAME bash -c 'source $VENV_PATH/bin/activate && python3 $BOT_FILE'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Ask to start
read -p "❓ Czy chcesz teraz uruchomić bota? (t/n): " confirm
if [[ $confirm == [tTjJ]* ]]; then
    ./update_bot.sh
fi

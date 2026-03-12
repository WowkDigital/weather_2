#!/bin/bash

# Configuration
SESSION_NAME="weather_bot"
BOT_FILE="main.py"
ENV_FILE=".env"
ENV_EXAMPLE=".env.example"

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "        🚀 WEATHER BOT INSTALLATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Anchor to script directory
cd "$(dirname "$0")"

# 2. Check for system dependencies
echo "🔍 Checking system dependencies..."
MISSING_DEPS=()
for cmd in python3 pip3 screen; do
    if ! command -v $cmd &> /dev/null; then
        MISSING_DEPS+=("$cmd")
    fi
done

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "⚠️  Missing packages: ${MISSING_DEPS[*]}"
    echo "💡 Try: sudo apt update && sudo apt install python3 python3-pip python3-venv screen -y"
fi

# 3. Create Virtual Environment
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "⏳ Creating virtual environment (venv)..."
    if python3 -m venv venv; then
        echo "✅ venv created."
        VENV_PATH="venv"
    else
        echo "❌ ERROR: Failed to create venv. Check if python3-venv is installed."
        exit 1
    fi
else
    echo "✅ Virtual environment already exists."
    [ -d "venv" ] && VENV_PATH="venv" || VENV_PATH=".venv"
fi

# 4. Install Dependencies
echo "⏳ Installing dependencies from requirements.txt..."
if $VENV_PATH/bin/pip install --upgrade -r requirements.txt; then
    echo "✅ Dependencies installed successfully."
else
    echo "❌ ERROR: Failed to install dependencies."
    echo "💡 Try manually: source $VENV_PATH/bin/activate && pip install python-telegram-bot[job-queue] APScheduler --upgrade"
    exit 1
fi

# 5. Setup .env file
if [ ! -f "$ENV_FILE" ]; then
    echo "📄 Configuring .env file..."
    if [ -f "$ENV_EXAMPLE" ]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        echo "✅ Copied $ENV_EXAMPLE to $ENV_FILE."
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "⚠️  NOTICE: You must now provide your API keys in the .env file"
        echo "Provide TELEGRAM_BOT_TOKEN (or press Enter to skip):"
        read -r bot_token
        if [ -n "$bot_token" ]; then
            sed -i "s|YOUR_TELEGRAM_BOT_TOKEN|$bot_token|" "$ENV_FILE"
        fi
        
        echo "Provide WEATHER_API_KEY (or press Enter to skip):"
        read -r api_key
        if [ -n "$api_key" ]; then
            sed -i "s|YOUR_WEATHER_API_KEY|$api_key|" "$ENV_FILE"
        fi
        echo "✅ Updated $ENV_FILE."
    else
        echo "⚠️  NOTICE: $ENV_EXAMPLE not found. Please create .env file manually."
    fi
else
    echo "✅ .env file already exists."
fi

# 6. Final message
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ✨ Installation completed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 🚀 To start the bot now, type:"
echo "    ./update_bot.sh"
echo ""
echo " 📈 To start manually in screen:"
echo "    screen -dmS $SESSION_NAME bash -c 'source $VENV_PATH/bin/activate && python3 $BOT_FILE'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Ask to start
read -p "❓ Do you want to start the bot now? (y/n): " confirm
if [[ $confirm == [yYjJ]* ]]; then
    ./update_bot.sh
fi

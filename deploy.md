# Telegram Weather MVP Bot - Deployment onto Ubuntu (Google Cloud)

This guide will help you install and run your bot on an Ubuntu server (e.g., Google Cloud) using `screen` to keep the process running after you close the terminal.

## 1. System Requirements and Updates

Connect to your Ubuntu machine using SSH, then verify necessary packages:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv screen -y
```

## 2. Setting up the Project Folder

Clone your repository directly onto the server using Git:

```bash
cd ~
git clone https://github.com/WowkDigital/weather_2
cd weather_2
chmod +x install.sh update_bot.sh
./install.sh
```

The `install.sh` script will:
- Check for system dependencies.
- Create a virtual environment (`venv`).
- Install Python dependencies.
- Help you configure the `.env` file.
- Offer to start the bot.

## 4. Setting up the `.env` file

Since your `.env` file is likely ignored by Git (for security), you need to create it on the server. You can copy it from the template:

```bash
cp .env.example .env
nano .env
```
Inside the `nano` editor, paste your real tokens, then press `Ctrl+O` (Enter) to save and `Ctrl+X` to exit.

## 5. Running the bot using Screen

A tool called `screen` allows you to open a terminal session that stays alive even if you disconnect from SSH.

```bash
# Start a new screen session and name it "weatherbot"
screen -S weatherbot

# Make sure you are in the directory and the environment is active
cd ~/weather_2
source venv/bin/activate

# Run the python script
python3 main.py
```

The bot should now say `Bot is starting...`

## 6. Exiting your Screen safely

To leave the screen session running in the background, press the following keyboard combination:
`Ctrl + A` and then press `D`
(This DETACHES the screen, keeping the script running).

You can now safely exit your SSH session.

## 7. Useful Screen Commands

- To check running screens:
  `screen -ls`

- To return to your bot's screen later:
  `screen -r weatherbot`

- To stop the bot entirely:
  Attach the screen using `screen -r weatherbot` and press `Ctrl + C`
  To kill the screen entirely, you can type `exit` after pressing `Ctrl + C`.

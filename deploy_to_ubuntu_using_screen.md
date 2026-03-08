# Telegram Weather MVP Bot - Deployment onto Ubuntu (Google Cloud)

This guide will help you install and run your bot on an Ubuntu server (e.g., Google Cloud) using `screen` to keep the process running after you close the terminal.

## 1. System Requirements and Updates

Connect to your Ubuntu machine using SSH, then verify necessary packages:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv screen -y
```

## 2. Setting up the Project Folder

Create a folder for the deployment and move your code into it:

```bash
mkdir ~/weather_bot
cd ~/weather_bot
```

Upload your `main.py`, `requirements.txt`, and `.env` files here (you can use SFTP, `scp`, or clone a Git repository).

## 3. Creating a Virtual Environment
It's highly recommended to use a virtual environment in Python:

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
```

## 4. Setting up the `.env` file

Ensure your `.env` file is present in the `~/weather_bot` folder and looks like this (with your real keys):

```env
TELEGRAM_BOT_TOKEN=your_real_telegram_bot_token_here
WEATHER_API_KEY=your_real_weatherapi_key_here
```

Keep this `.env` file secure to prevent others from using your APIs.

## 5. Running the bot using Screen

A tool called `screen` allows you to open a terminal session that stays alive even if you disconnect from SSH.

```bash
# Start a new screen session and name it "weatherbot"
screen -S weatherbot

# Make sure you are in the directory and the environment is active
cd ~/weather_bot
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

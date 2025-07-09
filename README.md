# Valorant Discord Bot
A Python Discord bot for retrieving and posting new Valorant patch notes and post-match Reddit threads to a designated channel.

## Installation

Ensure you have the following installed:
- Python 3.10+
- Discord application and bot
- Reddit application
- Linux server (optional) 

Run the following commands in the directory where you want to install the bot:

```bash
git clone https://github.com/dsmaster1/valorant-discord-bot.git
cd valorant-discord-bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a .env file in the root directory with the following values:
```ini
DISCORD_TOKEN=[bot_token]
DISCORD_GUILD_ID=[server_id]
MAIN_CHANNEL_ID=[channel_id]
LAST_PATCHNOTE_FILE=[default: last_patchnote.json]
REDDIT_CLIENT_ID=[app_client_id]
REDDIT_CLIENT_SECRET=[app_secret]
REDDIT_USER_AGENT=[script:(YOUR_APP)/1.0 by u/(YOUR_USERNAME)]
POSTED_THREADS_FILE=[default: posted_threads.json]
```

Secure it:
```bash
chmod 600 .env
chown YOUR_USERNAME:YOUR_USERNAME .env
```

## Usage

```bash
.venv/bin/python bot/discord_bot.py
```

## Hosting on a Linux Server
Create a file at:
`/etc/systemd/system/valorant-discord-bot.service`

```ini
[Unit]
Description=Valorant Discord Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/valorant-discord-bot
ExecStart=/home/YOUR_USERNAME/valorant-discord-bot/.venv/bin/python3 bot/discord_bot.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Secure it with:
```bash
sudo chmod 644 /etc/systemd/system/valorant-discord-bot.service
```

Enable and start the bot:
```bash
sudo systemctl daemon-reexec # reload systemd if needed
sudo systemctl daemon-reload # reload unit files
sudo systemctl enable valorant-discord-bot
sudo systemctl start valorant-discord-bot
```

Check status and logs:
```bash
sudo systemctl status valorant-discord-bot
journalctl -u valorant-discord-bot -e
```

Manual deploy script: `deploy.sh`
```bash
#!/bin/bash
cd valorant-discord-bot/ || exit
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart valorant-discord-bot
```
Make it executable:
```bash
chmod +x deploy.sh
```

## Version History
* 0.1
    * Initial Release
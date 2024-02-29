# Socialite - Create a social graph of mutual connections on Telegram 

Note: Socialite has won first place and the highest prize pool allocation as part of a hackathon (https://twitter.com/viaprize/status/1711985384530616788)

## A telegram bot written in Python, using Neo4j as a GDBMS backend database
Socialite is a Python script for a Telegram bot that allows users to join a social graph by sending requests to connect with others. The bot uses the py2neo library to interact with a Neo4j database hosted on Neo4j AuraDB, storing and managing connections between users.

## How to Deploy and Install:
Prerequisites:
- Python 3.6+
- python-telegram-bot py2neo

Telegram Bot Setup:
1. Obtain a Telegram bot token obtained from BotFather.
2. Replace TOKEN in bot.py with your Telegram bot token.

Neo4j Database Setup:
1. Use Neo4j AuraDB as a managed database
2. Configure Neo4j AuraDB connection details (DB_URI, PORT_NUMBER, DB-USER, DB-PASSWORD).

Running the Bot:
Execute the script:
python bot.py

Using the Bot:
The bot will start polling for updates and respond to commands:
- /start will start the bot
- /request @[telegram handle] will send a connection request to a telegram user
-/graph will send a link to open up a web-hosted html of your social graph

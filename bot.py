import discord
import os
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()  # Load .env file
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == 'ping':
        await message.channel.send('pong!')

keep_alive()  # Start web server to keep bot alive
client.run(TOKEN)

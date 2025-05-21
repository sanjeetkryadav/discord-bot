import discord
import os
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

print(f"Bot Token: {TOKEN}")  # Debug: Check if token is correct

intents = discord.Intents.default()
intents.message_content = True  # Ensure we can read message content

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')  # Confirm login

@client.event
async def on_message(message):
    print(f"Received message: {message.content}")  # Debug: Log the received message
    if message.author == client.user:
        return

    if message.content.lower() == 'ping':
        print("Pong response triggered!")  # Debug: Check if ping condition is met
        await message.channel.send('pong!')

    if message.content.lower() == 'hello':
        print("Pong response triggered!")  # Debug: Check if ping condition is met
        await message.channel.send('hello there!')

@client.event
async def on_error(event, *args, **kwargs):
    print(f"Error occurred: {event}, {args}, {kwargs}")  # Catch and print errors

keep_alive()
client.run(TOKEN)

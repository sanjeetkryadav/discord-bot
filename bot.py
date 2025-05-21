import discord
import os
import re
from dotenv import load_dotenv
from keep_alive import keep_alive
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)
# Slash command tree
tree = bot.tree

client = discord.Client(intents=intents)

# Map words/symbols to operations and emojis
OPERATIONS = {
    '+': ('add', '➕'),
    'add': ('add', '➕'),
    '-': ('subtract', '➖'),
    'subtract': ('subtract', '➖'),
    '*': ('multiply', '✖️'),
    'x': ('multiply', '✖️'),
    'multiply': ('multiply', '✖️'),
    '/': ('divide', '➗'),
    'divide': ('divide', '➗'),
    '÷': ('divide', '➗'),
}

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    print(f"Received message: {message.content}")  # Debug: Log the received message
    if message.author == client.user:
        return

    if message.content.lower() == 'ping':
        print("Pong response triggered!")  # Debug: Check if ping condition is met
        await message.channel.send('pong!')

    if message.content.lower() == 'hello':
        print("Pong response triggered!")  # Debug: Check if ping condition is met
        await message.channel.send('hello there!')

    content = message.content.lower()

    # Try to find an arithmetic expression
    match = re.search(r'(-?\d+(?:\.\d+)?)\s*([+/*x\-]|add|subtract|divide|multiply)\s*(-?\d+(?:\.\d+)?)', content)
    if not match:
        return

    num1, op_raw, num2 = match.groups()
    num1, num2 = float(num1), float(num2)

    operation = OPERATIONS.get(op_raw.strip())
    if not operation:
        return

    op_name, emoji = operation

    await message.add_reaction(emoji)

    def check(reaction, user):
        return (
            user == message.author and
            str(reaction.emoji) == emoji and
            reaction.message.id == message.id
        )

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=check)
        result = None
        if op_name == 'add':
            result = num1 + num2
        elif op_name == 'subtract':
            result = num1 - num2
        elif op_name == 'multiply':
            result = num1 * num2
        elif op_name == 'divide':
            if num2 == 0:
                result = "❌ Cannot divide by zero!"
            else:
                result = num1 / num2

        await message.channel.send(f"🧮 Result: `{num1} {op_raw} {num2} = {result}`")
    except Exception as e:
        print("⏱️ Reaction timeout or error:", e)

# ✅ Slash command: /math
@tree.command(name="math", description="Solve a math expression like 5+2 or 10 divide 2")
async def math_command(interaction: discord.Interaction, expression: str):
    await interaction.response.defer()
    match = re.search(r'(-?\d+(?:\.\d+)?)\s*([+/*x\-]|add|subtract|divide|multiply)\s*(-?\d+(?:\.\d+)?)', expression.lower())
    if not match:
        await interaction.followup.send("❌ Invalid expression. Example: `5 + 3` or `10 divide 2`")
        return

    num1, op_raw, num2 = match.groups()
    num1, num2 = float(num1), float(num2)

    operation = OPERATIONS.get(op_raw.strip())
    if not operation:
        await interaction.followup.send("❌ Unsupported operation.")
        return

    op_name, emoji = operation

    if op_name == 'add':
        result = num1 + num2
    elif op_name == 'subtract':
        result = num1 - num2
    elif op_name == 'multiply':
        result = num1 * num2
    elif op_name == 'divide':
        if num2 == 0:
            result = "❌ Cannot divide by zero!"
        else:
            result = num1 / num2

    await interaction.followup.send(f"{emoji} `{num1} {op_raw} {num2} = {result}`")



keep_alive()
client.run(TOKEN)

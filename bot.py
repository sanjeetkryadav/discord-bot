import discord
import os
import re
from dotenv import load_dotenv
from keep_alive import keep_alive
from discord.ext import commands
import discord.app_commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ✅ Full intents
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.dm_messages = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
#slash cmd tree
tree = bot.tree

OPERATIONS = {
    '+': ('add', '➕'),
    'add': ('add', '➕'),
    '-': ('subtract', '➖'),
    'subtract': ('subtract', '➖'),
    '*': ('multiply', '✖️'),
    'x': ('multiply', '✖️'),
    'multiply': ('multiply', '✖️'),
    '/': ('divide', '➗'),
    '÷': ('divide', '➗'),
    'divide': ('divide', '➗'),
}

def format_result(num1, num2, result, op_raw):
    # Check if both inputs are integers
    is_int_input = num1.is_integer() and num2.is_integer()
    
    # Format the result based on whether it's an integer and inputs were integers
    if isinstance(result, (int, float)):
        if result.is_integer() and is_int_input:
            result = int(result)
        return f"🧮 Result: `{int(num1) if num1.is_integer() else num1} {op_raw} {int(num2) if num2.is_integer() else num2} = {result}`"
    return f"🧮 Result: `{num1} {op_raw} {num2} = {result}`"

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()

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
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
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

        await message.channel.send(format_result(num1, num2, result, op_raw))
    except Exception as e:
        print("⏱️ Reaction timeout or error:", e)

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(name="math",description="Solve a math expression like 5+2 or 10 divide 2")
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

    await interaction.followup.send(format_result(num1, num2, result, op_raw))

keep_alive()
bot.run(TOKEN)

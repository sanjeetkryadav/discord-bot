import discord
import os
import re
import random
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from keep_alive import keep_alive
from discord.ext import commands
import discord.app_commands
from googletrans import Translator

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

# Store reminders
reminders = {}

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

@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(name="random", description="Generate a random number between two values")
async def random_command(interaction: discord.Interaction, min_value: int, max_value: int):
    if min_value >= max_value:
        await interaction.response.send_message("❌ Minimum value must be less than maximum value!")
        return
    
    number = random.randint(min_value, max_value)
    await interaction.response.send_message(f"🎲 Random number between {min_value} and {max_value}: `{number}`")


@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(name="remind", description="Set a reminder (time in minutes)")
async def remind_command(interaction: discord.Interaction, minutes: int, reminder: str):
    if minutes <= 0:
        await interaction.response.send_message("❌ Please provide a positive number of minutes!")
        return
    
    reminder_time = datetime.now() + timedelta(minutes=minutes)
    reminder_id = f"{interaction.user.id}_{reminder_time.timestamp()}"
    
    reminders[reminder_id] = {
        "user_id": interaction.user.id,
        "channel_id": interaction.channel_id,
        "reminder": reminder,
        "time": reminder_time
    }
    
    await interaction.response.send_message(
        f"⏰ I'll remind you in {minutes} minutes about: {reminder}"
    )
    
    await asyncio.sleep(minutes * 60)
    
    if reminder_id in reminders:
        channel = bot.get_channel(reminders[reminder_id]["channel_id"])
        if channel:
            await channel.send(f"⏰ <@{interaction.user.id}> Reminder: {reminder}")
        del reminders[reminder_id]


@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(name="translate", description="Translate text to another language")
async def translate_command(interaction: discord.Interaction, text: str, target_language: str = "en"):
    await interaction.response.defer()
    
    try:
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        
        await interaction.followup.send(
            f"🌐 Translation:\n"
            f"Original ({translation.src}): `{text}`\n"
            f"Translated ({translation.dest}): `{translation.text}`"
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Translation failed: {str(e)}")

@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(name="flip", description="Flip a coin")
async def flip_command(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"🪙 The coin landed on: `{result}`")

@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(name="roll", description="Roll dice (e.g., 2d6 for two six-sided dice)")
async def roll_command(interaction: discord.Interaction, dice: str):
    try:
        # Parse dice notation (e.g., "2d6")
        num_dice, sides = map(int, dice.lower().split('d'))
        
        if num_dice <= 0 or sides <= 0:
            await interaction.response.send_message("❌ Please provide valid dice numbers!")
            return
        
        if num_dice > 100:
            await interaction.response.send_message("❌ Maximum 100 dice at once!")
            return
        
        if sides > 100:
            await interaction.response.send_message("❌ Maximum 100 sides per die!")
            return
        
        # Roll the dice
        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        total = sum(rolls)
        
        # Format the response
        if num_dice == 1:
            response = f"🎲 You rolled: `{rolls[0]}`"
        else:
            response = f"🎲 You rolled: `{', '.join(map(str, rolls))}`\nTotal: `{total}`"
        
        await interaction.response.send_message(response)
        
    except ValueError:
        await interaction.response.send_message(
            "❌ Invalid dice notation! Use format like '2d6' for two six-sided dice."
        )

keep_alive()
bot.run(TOKEN)

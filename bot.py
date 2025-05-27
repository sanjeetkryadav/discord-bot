import discord
import os
import re
import random
import asyncio
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from keep_alive import keep_alive
from discord.ext import commands
import discord.app_commands
from googletrans import Translator
from pytz import timezone

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

# Timezone settings
IST = timezone('Asia/Kolkata')

def get_ist_time():
    """Get current time in IST"""
    return datetime.now(IST)

def format_datetime(dt_str):
    """Convert datetime string to IST and format it"""
    try:
        # Parse the datetime string
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        # Make it timezone aware
        dt = IST.localize(dt)
        # Format as "DD/MM/YYYY HH:MM"
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return dt_str

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    
    # Drop the existing table to recreate it with the new structure
    c.execute('DROP TABLE IF EXISTS notes')
    
    # Create notes table with a composite unique constraint
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id, user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database when bot starts
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    init_db()
    try:
        synced = await tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

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
async def on_message(message):
    if message.author.bot:
        return

    # Check for password generator command
    if message.content.startswith('!password'):
        try:
            # Default values
            length = 12
            use_uppercase = True
            use_numbers = True
            use_symbols = True
            
            # Parse arguments if provided
            args = message.content.split()
            if len(args) > 1:
                try:
                    length = int(args[1])
                    if length < 8 or length > 32:
                        await message.channel.send("❌ Password length must be between 8 and 32 characters!")
                        return
                except ValueError:
                    await message.channel.send("❌ Invalid length! Usage: `!password [length]`")
                    return

            # Character sets
            lowercase = 'abcdefghijklmnopqrstuvwxyz'
            uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            numbers = '0123456789'
            symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?'

            # Build character pool
            chars = lowercase
            if use_uppercase:
                chars += uppercase
            if use_numbers:
                chars += numbers
            if use_symbols:
                chars += symbols

            # Generate password
            password = ''.join(random.choice(chars) for _ in range(length))
            
            # Ensure password meets requirements
            if use_uppercase and not any(c.isupper() for c in password):
                password = password[:-1] + random.choice(uppercase)
            if use_numbers and not any(c.isdigit() for c in password):
                password = password[:-1] + random.choice(numbers)
            if use_symbols and not any(c in symbols for c in password):
                password = password[:-1] + random.choice(symbols)

            # Send password in a code block
            await message.channel.send(f"🔐 Generated Password ({length} characters):\n```{password}```")
            
            # Delete the original command message for security
            await message.delete()
            return

        except Exception as e:
            await message.channel.send(f"❌ Error generating password: {str(e)}")
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
    
    # Try to create DM channel with user
    try:
        dm_channel = await interaction.user.create_dm()
    except discord.Forbidden:
        await interaction.response.send_message("❌ I cannot send you DMs! Please enable DMs from server members.")
        return
    except Exception as e:
        await interaction.response.send_message("❌ Failed to create DM channel. Please try again later.")
        return
    
    reminder_time = datetime.now() + timedelta(minutes=minutes)
    reminder_id = f"{interaction.user.id}_{reminder_time.timestamp()}"
    
    reminders[reminder_id] = {
        "user_id": interaction.user.id,
        "dm_channel": dm_channel,
        "reminder": reminder,
        "time": reminder_time
    }
    
    await interaction.response.send_message(
        f"🔔You'll be reminded in {minutes} mins: **{reminder}**"
         )
    
    await asyncio.sleep(minutes * 60)
    
    if reminder_id in reminders:
        try:
            await reminders[reminder_id]["dm_channel"].send(
                f"📝 **Reminder:** **{reminder}**"

            )
        except Exception as e:
            # If DM fails, try to notify in the original channel
            try:
                await interaction.channel.send(
                    f"❌ <@{interaction.user.id}> I couldn't send you a DM for your reminder: {reminder}"
                )
            except:
                pass  # If both DM and channel message fail, silently fail
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

@tree.command(name="note", description="Store a note with a title and content")
async def note_command(interaction: discord.Interaction, title: str, content: str):
    try:
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        
        # Get current time in IST
        current_time = get_ist_time().strftime('%Y-%m-%d %H:%M:%S')
        
        # Find the lowest available ID for this specific user
        c.execute('SELECT id FROM notes WHERE user_id = ? ORDER BY id', (interaction.user.id,))
        existing_ids = [row[0] for row in c.fetchall()]
        
        # Find the first gap in IDs for this user, or use 1 if no notes exist
        note_id = 1
        for existing_id in existing_ids:
            if existing_id != note_id:
                break
            note_id += 1
        
        # Insert the note with the specific ID
        c.execute(
            'INSERT INTO notes (id, user_id, title, content, created_at) VALUES (?, ?, ?, ?, ?)',
            (note_id, interaction.user.id, title, content, current_time)
        )
        
        conn.commit()
        
        # Format the time for display
        display_time = format_datetime(current_time)
        
        await interaction.response.send_message(
            f"📝 Note saved successfully!\n"
            f"Title: `{title}`\n"
            f"ID: `{note_id}`\n"
            f"Created: `{display_time}`"
        )
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to save note: {str(e)}")
    finally:
        conn.close()

@tree.command(name="notes", description="List all your notes")
async def notes_command(interaction: discord.Interaction):
    try:
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        
        # Get all notes for the user
        c.execute(
            'SELECT id, title, created_at FROM notes WHERE user_id = ? ORDER BY id',
            (interaction.user.id,)
        )
        
        notes = c.fetchall()
        
        if not notes:
            await interaction.response.send_message("📝 You don't have any notes yet!")
            return
        
        # Format the notes list
        notes_list = "📝 Your Notes:\n"
        for note_id, title, created_at in notes:
            formatted_time = format_datetime(created_at)
            notes_list += f"ID: `{note_id}` | Title: `{title}` | Created: {formatted_time}\n"
        
        await interaction.response.send_message(notes_list)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to fetch notes: {str(e)}")
    finally:
        conn.close()

@tree.command(name="viewnote", description="View a specific note by ID")
async def viewnote_command(interaction: discord.Interaction, note_id: int):
    try:
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        
        # Get the specific note for this user
        c.execute(
            'SELECT title, content, created_at FROM notes WHERE id = ? AND user_id = ?',
            (note_id, interaction.user.id)
        )
        
        note = c.fetchone()
        
        if not note:
            await interaction.response.send_message("❌ Note not found or you don't have permission to view it!")
            return
        
        title, content, created_at = note
        formatted_time = format_datetime(created_at)
        
        await interaction.response.send_message(
            f"📝 Note Details:\n"
            f"Title: `{title}`\n"
            f"Content: `{content}`\n"
            f"Created: {formatted_time}"
        )
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to fetch note: {str(e)}")
    finally:
        conn.close()

@tree.command(name="deletenote", description="Delete a note by ID")
async def deletenote_command(interaction: discord.Interaction, note_id: int):
    try:
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        
        # Delete the note for this specific user
        c.execute(
            'DELETE FROM notes WHERE id = ? AND user_id = ?',
            (note_id, interaction.user.id)
        )
        
        if c.rowcount == 0:
            await interaction.response.send_message("❌ Note not found or you don't have permission to delete it!")
            return
        
        conn.commit()
        await interaction.response.send_message(f"🗑️ Note `{note_id}` has been deleted!")
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to delete note: {str(e)}")
    finally:
        conn.close()

@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(name="myreminders", description="List all your active reminders")
async def myreminders_command(interaction: discord.Interaction):
    try:
        # Filter reminders for this user
        user_reminders = [
            (reminder_id, reminder_data)
            for reminder_id, reminder_data in reminders.items()
            if reminder_data["user_id"] == interaction.user.id
        ]
        
        if not user_reminders:
            await interaction.response.send_message("⏰ You don't have any active reminders!", ephemeral=True)
            return
        
        # Format the reminders list
        reminders_list = "⏰ Your Active Reminders:\n"
        for reminder_id, reminder_data in user_reminders:
            time_left = reminder_data["time"] - datetime.now()
            minutes_left = int(time_left.total_seconds() / 60)
            
            reminders_list += (
                f"• Reminder: `{reminder_data['reminder']}`\n"
                f"  Time left: `{minutes_left} minutes`\n"
            )
        
        await interaction.response.send_message(reminders_list, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to fetch reminders: {str(e)}", ephemeral=True)

keep_alive()
bot.run(TOKEN)

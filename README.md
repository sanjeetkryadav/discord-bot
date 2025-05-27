# Discord Bot

A versatile Discord bot with various utility commands including math operations, reminders, translations, and note-taking capabilities. The bot supports both slash commands and prefix commands for maximum flexibility.

## Features

- **Math Operations**: Solve basic math expressions using `/math` command
- **Random Number**: Generate random numbers between two values using `/random`
- **Reminders**: Set reminders with `/remind` and view active reminders with `/myreminders`
- **Translation**: Translate text to different languages using `/translate`
- **Coin Flip**: Flip a coin with `/flip`
- **Dice Roll**: Roll dice using `/roll` (e.g., "2d6")
- **Notes System**: 
  - Create notes with `/note`
  - List all notes with `/notes`
  - View specific notes with `/viewnote`
  - Delete notes with `/deletenote`
- **Password Generator**: Generate secure random passwords using `!password`
- **Help System**: View all available commands using `/help` or `!help`

## Command Types

### Slash Commands
All commands except `!password` and `!help` are implemented as slash commands for better user experience and Discord integration.

### Prefix Commands
- `!password [length]` - Generate a secure random password
  - Features:
    - Default length: 12 characters
    - Customizable length (8-32 characters)
    - Includes uppercase, lowercase, numbers, and symbols
    - Ensures password meets security requirements
    - Command message is automatically deleted for security
  - Usage:
    - `!password` - Generate a 12-character password
    - `!password 16` - Generate a 16-character password
- `!help` - Display all available commands in an organized embed
  - Shows all slash commands and prefix commands
  - Includes brief descriptions for each command
  - Organized by command type
  - Also available as `/help` slash command

## Setup

1. Clone the repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Discord bot token:
   ```
   DISCORD_TOKEN=your_token_here
   ```
4. Run the bot:
   ```
   python bot.py
   ```

## Requirements

- Python 3.8+
- discord.py
- python-dotenv
- googletrans
- pytz
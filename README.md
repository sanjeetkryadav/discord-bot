# Discord Bot with Math, Notes, and Utility Commands

A versatile Discord bot that provides mathematical calculations, note-taking capabilities, and various utility commands. The bot uses slash commands for easy interaction and includes features like reminders, translations, and random number generation.

## Features

### Math Operations
- Basic arithmetic operations (addition, subtraction, multiplication, division)
- Supports both slash commands and reaction-based calculations
- Handles both integer and decimal numbers
- Shows results in appropriate format (integers for whole numbers, decimals for fractional results)

### Note System
- Create, view, list, and delete personal notes
- User-specific note IDs (each user's notes start from ID 1)
- Timestamps in IST (Indian Standard Time)
- Notes are stored in a SQLite database

### Utility Commands
- Random number generation
- Reminders (sent to DMs)
- Text translation
- Coin flip
- Dice rolling

## Commands

### Math Commands
- `/math [expression]` - Solve a math expression (e.g., "5 + 3" or "10 divide 2")
- Reaction-based math: Type a math expression and react with the corresponding emoji

### Note Commands
- `/note [title] [content]` - Create a new note
- `/notes` - List all your notes
- `/viewnote [note_id]` - View a specific note
- `/deletenote [note_id]` - Delete a specific note

### Utility Commands
- `/random [min_value] [max_value]` - Generate a random number between two values
- `/remind [minutes] [reminder]` - Set a reminder (sent to DMs)
- `/myreminders` - To view active reminders
- `/translate [text] [target_language]` - Translate text to another language
- `/flip` - Flip a coin
- `/roll [dice]` - Roll dice (e.g., "2d6" for two six-sided dice)

## Setup

1. Clone the repository
2. Install required packages:
```bash
pip install discord.py python-dotenv googletrans==3.1.0a0 pytz
```

3. Create a `.env` file with your Discord bot token:
```
DISCORD_TOKEN=your_bot_token_here
```

4. Run the bot:
```bash
python bot.py
```

## Requirements
- Python 3.8 or higher
- discord.py
- python-dotenv
- googletrans
- pytz

## Features in Detail

### Math Operations
- Supports: +, -, *, /, add, subtract, multiply, divide
- Handles decimal numbers
- Shows results in appropriate format
- Works with both slash commands and reactions

### Note System
- Personal note storage
- User-specific note IDs
- IST timestamps
- SQLite database storage
- Secure (users can only access their own notes)

### Reminders
- Set reminders in minutes
- Reminders are sent to user's DMs
- Fallback to channel message if DM fails
- Clear error messages for DM issues

### Translation
- Translate text to any language
- Shows original and translated text
- Supports all languages available in Google Translate

### Random and Games
- Random number generation with range
- Coin flip (Heads/Tails)
- Dice rolling with custom notation (e.g., 2d6)

## Contributing
Feel free to submit issues and enhancement requests!

## License
This project is open source and available under the MIT License.
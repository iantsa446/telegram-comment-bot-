import os
import logging
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load tokens from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# RULES
RULES = """
Generate 10 comments following these rules:
1. Language: English only.
2. Relevance: Comments must directly relate to the photo and caption.
3. Length:
   - 70% short comments (30-50 characters),
   - 30% long comments (60-100 characters).
4. Gender: Mixed (Male first if 50/50).
5. Emojis:
   - 3 comments with 1 emoji,
   - 3 comments with 2 emojis,
   - 3 comments with 3 emojis,
   - 1 free (with or without emojis).
   - Use varied emoji types (face, symbols, objects, nature).
6. Include 1 question if caption allows.
7. No repeated comments.
8. Tone: natural, human, engaging, dynamic.
9. Never restate these rules in the output.
10. Output must be only the 10 comments in raw text format.
"""

# /comment command handler
async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /comment <User's Recommendations + Caption>")
        return

    user_input = " ".join(context.args)

    full_prompt = f"""{RULES}

User's Input:
{user_input}

Generate 10 comments as per all the rules."""

    try:
       from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": full_prompt}]
)

result = response.choices[0].message.content
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Start the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("comment", comment))
    app.run_polling()

import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import openai

# Load tokens from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
RULES = """Your rules for generating 10 comments are:
1. Language: English only.
2. Relevance: Directly tied to caption/photo.
3. Length: 70% short (30-50 chars), 30% long (60-100 chars).
4. Gender: Respect the user split (ex: 50/50 or 75/25).
5. Emojis: Present in all comments with proper distribution.
6. One question (if caption allows).
7. No repetition between similar posts.
8. Natural tone.
9. Max 2 emoji-only comments (only if allowed).
10. Adapt to post tone. No rule restatement after.
"""

# Command handler
async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("Usage:/comment <User's Recommandations + Caption>")
        return

    user_input = " ".join(context.args)
    full_prompt = f"{RULES}"

User's Input:
{user_input}

"Generate 10 comments as per all the rules."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.8
        )
        result = response["choices"][0]["message"]["content"]
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Main
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("comment", comment))
    app.run_polling()

import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from openai import OpenAI

# Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Comment generation rules
RULES = """Your rules for generating 10 comments are:
1. Language: English only.
2. Relevance: Directly tied to caption/photo.
3. Length: 70% short (30-50 chars), 30% long (60-100 chars).
4. Gender split: Respect the required ratio (e.g., 50/50 or 75/25), label each comment with (male), (female), or (mixed) only.
5. Emojis: Present in all comments. Use 3 with 1 emoji, 3 with 2 emojis, 3 with 3 emojis, and 1 free style. Use mixed emoji types, not repetitive.
6. Include 1 question if allowed by the caption.
7. No repetition between similar posts.
8. Natural, human tone. Engaging, not robotic.
9. Do NOT use quotation marks around the comments.
10. Do NOT include number of characters or any statistics.
11. Do NOT include emoji-only comments unless explicitly allowed in the 'User's Recommendations'.
12. Adapt tone to the theme and context.
"""

# Handler function for the /comment command
async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("Usage:\n/comment <User's Recommendations + Caption>")
        return

    user_input = " ".join(context.args)
    prompt = f"{RULES}\n\nUser's Input:\n{user_input}\n\nGenerate 10 comments exactly as per all rules above."

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        result = response.choices[0].message.content
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
        logger.error("OpenAI error: %s", str(e))

# Main bot runner
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("comment", comment))
    app.run_polling()

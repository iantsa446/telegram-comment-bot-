import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from PIL import Image
import requests
from io import BytesIO
import random

openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# === Comment Rules ===
RULES = {
    "language": "English",
    "short_percent": 0.7,
    "long_percent": 0.3,
    "gender_split": ["male", "female"],
    "emoji_distribution": [1, 2, 3],
    "require_emoji_in_all": True,
    "allow_hashtags": False,
    "allow_mentions": False,
    "emoji_only_comments": False,
    "question_count": 1,
    "no_char_count_displayed": True,
    "no_quotes": True,
    "male_first": True
}

# === Core Functions ===
def extract_image_and_caption(update: Update):
    photo = update.message.photo[-1].file_id if update.message.photo else None
    caption = update.message.caption or ""
    return photo, caption

def fetch_image_bytes(bot, file_id):
    newFile = bot.get_file(file_id)
    file = requests.get(newFile.file_path)
    return BytesIO(file.content)

def generate_prompt(caption):
    base_prompt = f"Generate 10 varied English Instagram comments based on this caption: {caption}."
    rule_str = (
        " Follow these rules strictly:"
        " 1. 70% short comments (5-50 chars), 30% long comments (60-100 chars)."
        " 2. Use exactly 3 comments with 1 emoji, 3 with 2 emojis, 3 with 3 emojis, and 1 free style."
        " 3. All comments must have at least 1 emoji."
        " 4. One comment must be a question (if caption allows)."
        " 5. No hashtags or mentions unless user explicitly allows."
        " 6. Gender split must be 50% male, 50% female with male first."
        " 7. Format: 1. (male) Comment here\n 2. (female) Comment here..."
        " 8. Do not use emoji-only comments."
        " 9. Do not display character counts."
        " 10. Do not use quotation marks."
    )
    return base_prompt + rule_str

async def generate_comments(image_bytes, caption):
    base64_image = base64.b64encode(image_bytes.getvalue()).decode("utf-8")
    response = openai.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates social media comments strictly based on visual content and user rules."},
            {"role": "user", "content": [
                {"type": "text", "text": generate_prompt(caption)},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        max_tokens=800
    )
    return response.choices[0].message.content

# === Telegram Handler ===
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo_id, caption = extract_image_and_caption(update)
        if not photo_id:
            await update.message.reply_text("Send an image with a caption.")
            return

        image_bytes = fetch_image_bytes(context.bot, photo_id)
        comments = await generate_comments(image_bytes, caption)
        await update.message.reply_text(comments)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# === Main Bot Launch ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    print("Bot started...")
    app.run_polling()

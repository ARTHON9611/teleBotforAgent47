import os
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Telegram Bot Token
TOKEN = os.getenv("TOKEN")

# API Base URL
API_URL = "https://agent47-zu3c.onrender.com"  # Update if deploying

# Setup logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Fetch Political News
async def news(update: Update, context: CallbackContext):
    response = requests.get(f"{API_URL}/news")
    news_data = response.json()
    
    if "headline" in news_data:
        await update.message.reply_text(f"📰 *{news_data['headline']}*\n{news_data['summary']}", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ No news available.")

# Generate Meme Caption
async def meme(update: Update, context: CallbackContext):
    response = requests.post(f"{API_URL}/generate_meme", json={"style": "funny"})

    if response.status_code != 200:
        await update.message.reply_text("⚠️ Error: Meme API is down.")
        return

    try:
        meme_caption = response.json().get("meme_caption", "Meme generation failed.")
        await update.message.reply_text(f"😂 Meme Caption: {meme_caption}")
    except requests.exceptions.JSONDecodeError:
        await update.message.reply_text("⚠️ Error: Invalid API response. Try again later.")

# Generate Meme Image
async def meme_image(update: Update, context: CallbackContext):
    response = requests.get(f"{API_URL}/meme_image")

    if response.status_code == 200:
        image_data = response.json()
        image_path = image_data.get("image")

        if image_path:
            await update.message.reply_photo(photo=open(image_path, "rb"))
        else:
            await update.message.reply_text("⚠️ Error: Meme image generation failed.")
    else:
        await update.message.reply_text("⚠️ Error: Meme API is down.")

# Fact Checking
async def fact_check(update: Update, context: CallbackContext):
    user_claim = " ".join(context.args)
    if not user_claim:
        await update.message.reply_text("Usage: /factcheck <claim>")
        return

    response = requests.post(f"{API_URL}/verify_claim", json={"claim": user_claim})
    fact_result = response.json().get("analysis", "Fact-checking failed.")
    
    await update.message.reply_text(f"✅ Fact-check result: {fact_result}")

# Start Command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🇺🇸 Meme & Fact Check Bot is live! Commands:\n"
        "/news - Latest political news\n"
        "/meme - Generate a meme caption\n"
        "/meme_image - Generate a meme image\n"
        "/factcheck <claim> - Verify a claim"
    )

# Main Function
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("meme", meme))
    app.add_handler(CommandHandler("meme_image", meme_image))
    app.add_handler(CommandHandler("factcheck", fact_check))

    app.run_polling()

if __name__ == "__main__":
    main()

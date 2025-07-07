import os
import logging
from yt_dlp import YoutubeDL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# === CONFIGURATION ===
TOKEN = "8004945612:AAH3GEDAR7SjJyfIXS2QoM7lOlBFRAl4BvA"  # Replace with your bot token
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === COMMAND: /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Start Downloading", callback_data="start")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to the Universal Downloader Bot!\nSend a link from TikTok, Instagram, YouTube, and more.",
        reply_markup=reply_markup
    )

# === COMMAND: /help ===
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *How to use:*\n"
        "1. Send a link from any supported platform (TikTok, YouTube, Instagram, etc.)\n"
        "2. Choose quality: 4K, 1080p, or Audio\n"
        "3. Receive your video or audio\n\n"
        "_Prepared by @a412ss_",
        parse_mode="Markdown"
    )

# === BUTTON HANDLER ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        await query.edit_message_text("📥 Please send a link to begin.")
    elif query.data == "help":
        await help_command(query, context)
    elif query.data.startswith("quality_"):
        quality = query.data.split("_")[1]
        url = context.user_data.get("last_url")

        if not url:
            await query.edit_message_text("⚠️ No link found. Please send a new one.")
            return

        await query.edit_message_text(f"⏳ Downloading in {quality.upper()}... Please wait.")
        await download_and_send(query, context, url, quality)

# === HANDLE LINKS ===
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if any(x in url for x in ["tiktok.com", "instagram.com", "youtu", "facebook.com", "twitter.com", "reddit.com", "pinterest.com", "soundcloud.com", "vimeo.com"]):
        context.user_data["last_url"] = url
        keyboard = [[
            InlineKeyboardButton("4K", callback_data="quality_4k"),
            InlineKeyboardButton("1080p", callback_data="quality_1080p"),
            InlineKeyboardButton("Audio", callback_data="quality_audio")
        ]]
        await update.message.reply_text("🎞 Choose quality:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("❌ Unsupported or invalid link. Try TikTok, Instagram, YouTube, etc.")

# === DOWNLOAD AND SEND ===
async def download_and_send(query, context, url, quality):
    format_map = {
        "4k": "bestvideo[height<=2160]+bestaudio/best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best",
        "audio": "bestaudio"
    }

    ydl_opts = {
        'format': format_map.get(quality, 'best'),
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title).50s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        caption = "✅ Done!\n_Prepared by @a412ss_"

        # Send video or audio
        if file_path.endswith(".mp3") or info.get("ext") == "m4a":
            with open(file_path, 'rb') as audio:
                await query.message.reply_audio(audio=audio, caption=caption, parse_mode="Markdown")
        else:
            with open(file_path, 'rb') as video:
                await query.message.reply_video(video=video, caption=caption, parse_mode="Markdown")

        os.remove(file_path)

    except Exception as e:
        logger.error(f"Download failed: {e}")
        await query.message.reply_text("❌ Failed to download. Try another link.")

# === MAIN ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

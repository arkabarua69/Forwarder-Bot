import os
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ----------------- Load environment -----------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set!")

# ----------------- Flask app -----------------
app = Flask(__name__)
CORS(app)

# ----------------- Global variables -----------------
SOURCE_CHAT_ID = None
TARGET_CHAT_ID = None
logs = []
bot_thread = None
application = None  # global bot application


def log_message(msg: str):
    """Add message to log and print."""
    logs.append(msg)
    print(msg)


# ----------------- Telegram bot handler -----------------
async def forward_channel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward messages from source to target chat."""
    try:
        if update.message and update.message.chat.id == SOURCE_CHAT_ID:
            await context.bot.copy_message(
                chat_id=TARGET_CHAT_ID,
                from_chat_id=SOURCE_CHAT_ID,
                message_id=update.message.message_id,
            )
            log_message(f"Copied message ID {update.message.message_id} to target.")

        elif update.channel_post and update.channel_post.chat.id == SOURCE_CHAT_ID:
            await context.bot.copy_message(
                chat_id=TARGET_CHAT_ID,
                from_chat_id=SOURCE_CHAT_ID,
                message_id=update.channel_post.message_id,
            )
            log_message(
                f"Copied channel post ID {update.channel_post.message_id} to target."
            )

    except Exception as e:
        log_message(f"Error copying message: {e}")


# ----------------- Bot runner -----------------
def run_bot():
    global application
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL, forward_channel_message))
    log_message("Bot is running...")
    # drop_pending_updates prevents conflicts with previous bot sessions
    application.run_polling(drop_pending_updates=True)


# ----------------- Flask endpoints -----------------
@app.route("/start", methods=["POST"])
def start():
    """Start the bot with given source and target chat IDs."""
    global SOURCE_CHAT_ID, TARGET_CHAT_ID
    data = request.get_json()

    if not data or "source" not in data or "target" not in data:
        return jsonify({"message": "Missing source or target chat ID"}), 400

    try:
        SOURCE_CHAT_ID = int(data["source"])
        TARGET_CHAT_ID = int(data["target"])
    except ValueError:
        return jsonify({"message": "Invalid chat IDs"}), 400

    log_message(f"Bot started with Source: {SOURCE_CHAT_ID}, Target: {TARGET_CHAT_ID}")
    return jsonify({"message": "Bot started successfully!"})


@app.route("/logs", methods=["GET"])
def get_logs():
    """Return logs of forwarded messages."""
    return jsonify({"logs": logs})


if __name__ == "__main__":
    # Start Flask in a separate thread (daemon)
    flask_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))),
        daemon=True,
    )
    flask_thread.start()

    # Run the Telegram bot in the main thread
    run_bot()

import os
import subprocess
import json
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ApplicationBuilder, ContextTypes

app = Flask(__name__)
API_TOKEN = 'YOUR_MANAGER_BOT_TOKEN'
ADMIN_USER_ID = 'YOUR_TELEGRAM_USER_ID'
BOT_PATH = "/path/to/your/bots"
LOG_PATH = "/path/to/logs"

def load_user_settings():
    if not os.path.exists("user_settings.json"):
        with open("user_settings.json", "w") as f:
            f.write("{}")
    with open("user_settings.json", "r") as f:
        return json.load(f)

def save_user_settings(data):
    with open("user_settings.json", "w") as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("আপনি অনুমোদিত ব্যবহারকারী নন!")
        return

    keyboard = [
        [InlineKeyboardButton("➕ নতুন বট যোগ করুন", callback_data='add_bot')],
        [InlineKeyboardButton("✏️ কোড এডিট করুন", callback_data='edit_code')],
        [InlineKeyboardButton("📝 লগ ডাউনলোড করুন", callback_data='download_log')],
        [InlineKeyboardButton("🔄 বট রিস্টার্ট করুন", callback_data='restart_bot')],
        [InlineKeyboardButton("📜 বট তালিকা", callback_data='list_bots')],
        [InlineKeyboardButton("⚙️ সেটিংস", callback_data='settings')],
        [InlineKeyboardButton("👤 বট ওউনারস", callback_data='manage_owners')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("বট পরিচালনা মেনুতে স্বাগতম!", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'add_bot':
        await query.message.reply_text("নতুন বট যোগ করতে: /add_bot <bot_name> <bot_token>")
    elif query.data == 'edit_code':
        await query.message.reply_text("কোড সম্পাদনা করতে: /edit_code <bot_name>")
    elif query.data == 'download_log':
        await query.message.reply_text("লগ ডাউনলোড করতে: /download_log <bot_name>")
    elif query.data == 'restart_bot':
        await query.message.reply_text("বট রিস্টার্ট করতে: /restart_bot <bot_name>")
    elif query.data == 'list_bots':
        bot_list = "\n".join(os.listdir(BOT_PATH))
        await query.message.reply_text(f"যুক্ত করা বটসমূহ:\n{bot_list}")
    elif query.data == 'settings':
        settings = load_user_settings()
        await query.message.reply_text(f"বর্তমান সেটিংস:\n{json.dumps(settings, indent=2)}")
    elif query.data == 'manage_owners':
        await query.message.reply_text("বট ওউনার পরিচালনা করতে: /add_owner <user_id>")

async def add_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("ব্যবহার: /add_owner <user_id>")
        return
    user_id = context.args[0]
    settings = load_user_settings()
    owners = settings.get("owners", [])
    if user_id not in owners:
        owners.append(user_id)
    settings["owners"] = owners
    save_user_settings(settings)
    await update.message.reply_text(f"User {user_id} সফলভাবে ওউনার হিসেবে যোগ হয়েছে।")

# বাকি কমান্ডগুলোও এখানে যুক্ত করতে পারেন...

def main():
    telegram_app = ApplicationBuilder().token(API_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("add_owner", add_owner))
    # অন্যান্য হ্যান্ডলারও যুক্ত করুন...
    telegram_app.add_handler(CallbackQueryHandler(button_handler))
    telegram_app.run_polling()

@app.route('/')
def home():
    return "Bot Manager is running!"

if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=5000)  # এখানে Flask পোর্ট সেট করা হয়েছে

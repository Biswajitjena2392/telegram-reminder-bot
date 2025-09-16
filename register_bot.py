import os
import json
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


# --- Telegram Bot Setup ---
load_dotenv()  # load .env file

# --- Google Sheets Setup ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Load JSON from env
google_creds_json = os.getenv("GOOGLE_CREDS")
creds_dict = json.loads(google_creds_json)

# Build credentials object from dict
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

# Authorize gspread
client = gspread.authorize(creds)

# Replace with your Google Sheet ID
SHEET_ID = os.getenv("SHEET_ID")
sheet = client.open_by_key(SHEET_ID).worksheet("RegisteredUsers")


BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send /register to sign up for reminders.")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = str(update.effective_chat.id)
    print(f"👉 Registered {user.username} with chat_id {chat_id}")
    # Fetch all ChatIDs already stored
    existing_ids = sheet.col_values(2)  # Column B = ChatID

    if chat_id in existing_ids:
        await update.message.reply_text("⚠️ You’re already registered for reminders.")
    else:
        sheet.append_row([user.username or "NoUsername", chat_id])
        await update.message.reply_text(f"✅ Registered! You'll now get reminders.\nYour ChatID: {chat_id}")
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))

    print("🤖 Bot running... press Ctrl+C to stop")
    app.run_polling()

if __name__ == "__main__":
    main()

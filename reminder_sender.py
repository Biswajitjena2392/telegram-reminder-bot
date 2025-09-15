import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application, ContextTypes
import gspread
from gspread import service_account, service_account_from_dict
from dotenv import load_dotenv
import os
import asyncio
import json


load_dotenv()
# ---------------- Google Sheets Setup ----------------
creds = json.loads(os.getenv("GOOGLE_CREDS"))
client = service_account_from_dict(creds)

SHEET_ID = os.getenv("SHEET_ID")
registered_sheet = client.open_by_key(SHEET_ID).worksheet("RegisteredUsers")
cases_sheet = client.open_by_key(SHEET_ID).worksheet("Cases")

BOT_TOKEN = os.getenv("BOT_TOKEN")
print("Loaded BOT_TOKEN:", BOT_TOKEN)

# ---------------- Reminder Function ----------------
async def send_reminders(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.date.today().strftime("%d-%b-%Y")  # Match sheet format

    # Get cases for today
    cases = cases_sheet.get_all_records(expected_headers=["Date", "Case"], head=2)
    todays_cases = [case["Case"] for case in cases if case["Date"] == today]

    if not todays_cases:
        print("No cases for today")
        return

    reminder_text = "📌 *Today's Cases*:\n" + "\n".join([f"- {c}" for c in todays_cases])

    registered_users = registered_sheet.get_all_records()
    for user in registered_users:
        chat_id = int(user["ChatID"])
        try:
            await context.bot.send_message(chat_id=chat_id, text=reminder_text, parse_mode="Markdown")
            print(f"✅ Sent to {chat_id}")
        except Exception as e:
            print(f"❌ Could not send to {chat_id}: {e}")

# ---------------- Bot Setup ----------------
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
    scheduler.add_job(send_reminders, "cron", hour=8, minute=0, args=[app.bot])
    scheduler.start()

    print("🤖 Bot running... press Ctrl+C to stop")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())

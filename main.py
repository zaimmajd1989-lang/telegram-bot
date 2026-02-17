import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TOKEN, ADMINS

def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    keyboard = []

    for cat in data["categories"]:
        keyboard.append([InlineKeyboardButton(cat, callback_data=f"cat:{cat}")])

    if update.effective_user.id in ADMINS:
        keyboard.append([InlineKeyboardButton("⚙️ لوحة التحكم", callback_data="admin")])

    await update.message.reply_text(
        data["welcome"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()

    if query.data.startswith("cat:"):
        cat = query.data.split(":")[1]
        buttons = []

        for name, link in data["categories"][cat].items():
            buttons.append([InlineKeyboardButton(name, url=link)])

        buttons.append([InlineKeyboardButton("⬅️ رجوع", callback_data="back")])

        await query.edit_message_text(
            f"اختر من {cat}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif query.data == "back":
        keyboard = []
        for cat in data["categories"]:
            keyboard.append([InlineKeyboardButton(cat, callback_data=f"cat:{cat}")])

        if query.from_user.id in ADMINS:
            keyboard.append([InlineKeyboardButton("⚙️ لوحة التحكم", callback_data="admin")])

        await query.edit_message_text(
            data["welcome"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "admin":
        if query.from_user.id not in ADMINS:
            return

        await query.edit_message_text("لوحة التحكم قيد التطوير")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

print("Bot running...")
app.run_polling()

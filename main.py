import json
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, MenuButtonCommands
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from config import TOKEN, ADMINS

user_state = {}

def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main_menu(data, is_admin=False):
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat:{cat}")]
                for cat in data["categories"]]

    if is_admin:
        keyboard.append([InlineKeyboardButton("⚙️ لوحة التحكم", callback_data="admin")])

    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    await update.message.reply_text(
        data["welcome"],
        reply_markup=main_menu(data, update.effective_user.id in ADMINS)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    uid = query.from_user.id

    if query.data.startswith("cat:"):
        cat = query.data.split(":")[1]
        buttons = [[InlineKeyboardButton(n, url=l)]
                   for n, l in data["categories"][cat].items()]
        buttons.append([InlineKeyboardButton("⬅️ رجوع", callback_data="back")])
        await query.edit_message_text(
            f"اختر من {cat}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif query.data == "back":
        await query.edit_message_text(
            data["welcome"],
            reply_markup=main_menu(data, uid in ADMINS)
        )

    elif query.data == "admin" and uid in ADMINS:
        keyboard = [
            [InlineKeyboardButton("➕ اضافة قسم", callback_data="add_cat")],
            [InlineKeyboardButton("➖ حذف قسم", callback_data="del_cat")],
            [InlineKeyboardButton("➕ اضافة بوت داخل قسم", callback_data="add_bot")],
            [InlineKeyboardButton("➖ حذف بوت من قسم", callback_data="del_bot")],
            [InlineKeyboardButton("👑 اضافة ادمن", callback_data="add_admin")],
            [InlineKeyboardButton("✏️ تعديل رسالة الترحيب", callback_data="edit_welcome")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data="back")]
        ]
        await query.edit_message_text(
            "لوحة التحكم:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    else:
        user_state[uid] = query.data
        if query.data == "add_cat":
            await query.message.reply_text("ارسل اسم القسم الجديد")

        elif query.data == "del_cat":
            await query.message.reply_text("ارسل اسم القسم المراد حذفه")

        elif query.data == "add_bot":
            await query.message.reply_text(
                "ارسل بالشكل التالي:\nاسم القسم | اسم البوت | الرابط"
            )

        elif query.data == "del_bot":
            await query.message.reply_text(
                "ارسل بالشكل التالي:\nاسم القسم | اسم البوت"
            )

        elif query.data == "add_admin":
            await query.message.reply_text("ارسل ايدي الادمن")

        elif query.data == "edit_welcome":
            await query.message.reply_text("ارسل رسالة الترحيب الجديدة")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in ADMINS or uid not in user_state:
        return

    data = load_data()
    text = update.message.text
    state = user_state[uid]

    try:
        if state == "add_cat":
            data["categories"][text] = {}

        elif state == "del_cat":
            data["categories"].pop(text, None)

        elif state == "add_bot":
            cat, name, link = text.split("|")
            data["categories"][cat.strip()][name.strip()] = link.strip()

        elif state == "del_bot":
            cat, name = text.split("|")
            data["categories"][cat.strip()].pop(name.strip(), None)

        elif state == "add_admin":
            ADMINS.append(int(text))

        elif state == "edit_welcome":
            data["welcome"] = text

        save_data(data)
        await update.message.reply_text("✅ تم التنفيذ")

    except:
        await update.message.reply_text("❌ الصيغة غلط")

    del user_state[uid]


# ✅ هنا التعديل الوحيد (زر Start دائم + Menu دائم)
async def set_menu(app):
    # زر start دائم
    await app.bot.set_my_commands([
        ("start", "بدء البوت")
    ])

    # زر Menu دائم تحت الدردشة
    await app.bot.set_chat_menu_button(
        menu_button=MenuButtonCommands()
    )


app = Application.builder().token(TOKEN).build()
app.post_init = set_menu

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

print("Bot running...")
app.run_polling()

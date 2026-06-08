import logging
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ===================== CONFIG =====================
BOT_TOKEN = "8705798699:AAHKM-G2r3aVrZ-hgen2O94IVtyNnn4mYNE"
ADMIN_ID = 1003577393048  # Apna Telegram ID

DATA_FILE = "users.json"
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

# ===================== DATA =====================
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

def add_user(user):
    users = load_users()
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "name": user.full_name,
            "username": user.username or "",
            "joined": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        save_users(users)

# ===================== HANDLERS =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user)

    if user.id == ADMIN_ID:
        users = load_users()
        keyboard = [
            [
                InlineKeyboardButton("📤 Broadcast", callback_data="broadcast_menu"),
                InlineKeyboardButton("👥 Members", callback_data="members")
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data="stats"),
                InlineKeyboardButton("📅 Schedule", callback_data="schedule_menu")
            ],
            [
                InlineKeyboardButton("✅ Test Msg", callback_data="test_msg")
            ]
        ]
        await update.message.reply_text(
            f"👑 *Admin Panel - FinalStrike Bot*\n\n"
            f"👥 Total Members: *{len(users)}*\n"
            f"✅ Bot 24/7 chal raha hai!\n\n"
            f"👇 Kya karna hai?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            f"👑 *Welcome {user.first_name}!*\n\n"
            f"🎮 *𝐌𝐫➮ᖴɪɴᴀʟ乂𝚂ᴛʀɪᴋᴇ BOT*\n\n"
            f"✅ Aap registered ho gaye!\n"
            f"📢 Aapko automatically updates milenge.\n\n"
            f"@FinalStrike02",
            parse_mode="Markdown"
        )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("❌ Sirf admin!")
        return

    back = [[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
    users = load_users()

    if query.data == "members":
        text = f"👥 *Total Members: {len(users)}*\n\n"
        for i, (uid, u) in enumerate(list(users.items())[:20]):
            name = u.get("name", "?")
            username = f"@{u['username']}" if u.get("username") else "No username"
            text += f"{i+1}. *{name}* ({username})\n"
        if len(users) > 20:
            text += f"\n...aur {len(users)-20} aur members"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back))

    elif query.data == "stats":
        text = f"""
📊 *Bot Stats*

👥 Total Members: *{len(users)}*
✅ Status: *Running 24/7*
🤖 Bot: *@FinalStrike02*
📅 Date: *{datetime.now().strftime('%d/%m/%Y %H:%M')}*
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back))

    elif query.data == "broadcast_menu":
        keyboard = [
            [InlineKeyboardButton("📝 Text Bhejo", callback_data="bc_text")],
            [InlineKeyboardButton("🖼 Photo + Caption", callback_data="bc_photo")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
        ]
        await query.edit_message_text(
            "📤 *Broadcast Menu*\n\nKya bhejana hai?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "bc_text":
        context.user_data["mode"] = "broadcast_text"
        await query.edit_message_text(
            "✏️ *Broadcast Text*\n\nApna message type karo - main sab members ko bhej dunga!\n\n/cancel - cancel karne ke liye",
            parse_mode="Markdown"
        )

    elif query.data == "bc_photo":
        context.user_data["mode"] = "broadcast_photo"
        await query.edit_message_text(
            "🖼 *Photo Broadcast*\n\nPhoto bhejo caption ke saath!\n\n/cancel - cancel karne ke liye",
            parse_mode="Markdown"
        )

    elif query.data == "test_msg":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="✅ *Yeh test message hai!*\n\nBot sahi kaam kar raha hai.\n\n@FinalStrike02",
            parse_mode="Markdown"
        )
        await query.edit_message_text("✅ Test message aapko bheja!", reply_markup=InlineKeyboardMarkup(back))

    elif query.data == "schedule_menu":
        keyboard = [
            [InlineKeyboardButton("⏰ Har 30 Min", callback_data="sch_30")],
            [InlineKeyboardButton("⏰ Har 1 Ghanta", callback_data="sch_60")],
            [InlineKeyboardButton("⏰ Har 2 Ghante", callback_data="sch_120")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
        ]
        await query.edit_message_text(
            "📅 *Auto Schedule*\n\nKitne time baad auto message bhejun?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("sch_"):
        mins = int(query.data.replace("sch_", ""))
        context.user_data["schedule_mins"] = mins
        context.user_data["mode"] = "schedule_msg"
        await query.edit_message_text(
            f"✏️ *Schedule Message - Har {mins} min*\n\nWoh message type karo jo automatically bhejana hai:\n\n/cancel - cancel",
            parse_mode="Markdown"
        )

    elif query.data == "admin_back":
        keyboard = [
            [
                InlineKeyboardButton("📤 Broadcast", callback_data="broadcast_menu"),
                InlineKeyboardButton("👥 Members", callback_data="members")
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data="stats"),
                InlineKeyboardButton("📅 Schedule", callback_data="schedule_menu")
            ],
            [
                InlineKeyboardButton("✅ Test Msg", callback_data="test_msg")
            ]
        ]
        await query.edit_message_text(
            f"👑 *Admin Panel*\n\n👥 Members: *{len(users)}*\n✅ Bot chal raha hai!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ===================== MESSAGE HANDLER =====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user)

    if user.id != ADMIN_ID:
        await update.message.reply_text(
            "✅ Aapka message mila!\n📢 Updates ke liye wait karo.\n\n@FinalStrike02"
        )
        return

    mode = context.user_data.get("mode", "")

    if mode == "broadcast_text":
        msg = update.message.text
        users = load_users()
        sent = 0
        failed = 0
        status_msg = await update.message.reply_text(f"📤 Bhej raha hoon... 0/{len(users)}")

        for i, uid in enumerate(users):
            try:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=f"📢 *FinalStrike Update:*\n\n{msg}\n\n@FinalStrike02",
                    parse_mode="Markdown"
                )
                sent += 1
            except:
                failed += 1

            if (i+1) % 10 == 0:
                try:
                    await status_msg.edit_text(f"📤 Bhej raha hoon... {i+1}/{len(users)}")
                except:
                    pass

        context.user_data["mode"] = ""
        await status_msg.edit_text(
            f"✅ *Broadcast Complete!*\n\n"
            f"✅ Bheja: {sent}\n"
            f"❌ Failed: {failed}\n"
            f"👥 Total: {len(users)}"
        )

    elif mode == "schedule_msg":
        msg = update.message.text
        mins = context.user_data.get("schedule_mins", 30)
        secs = mins * 60

        async def auto_send(ctx):
            users = load_users()
            for uid in users:
                try:
                    await ctx.bot.send_message(
                        chat_id=int(uid),
                        text=f"📢 *FinalStrike Auto Update:*\n\n{msg}\n\n⏰ _{datetime.now().strftime('%H:%M')}_\n@FinalStrike02",
                        parse_mode="Markdown"
                    )
                except:
                    pass

        context.application.job_queue.run_repeating(auto_send, interval=secs, first=10)
        context.user_data["mode"] = ""
        await update.message.reply_text(
            f"✅ *Schedule Set!*\n\n"
            f"⏰ Har *{mins} minute* pe yeh message\n"
            f"👥 Sab members ko jayega\n"
            f"📅 24/7 chalta rahega!",
            parse_mode="Markdown"
        )

    elif mode == "broadcast_photo":
        await update.message.reply_text("⚠️ Photo ke saath caption bhejo!")
        context.user_data["mode"] = ""

    else:
        keyboard = [
            [
                InlineKeyboardButton("📤 Broadcast", callback_data="broadcast_menu"),
                InlineKeyboardButton("👥 Members", callback_data="members")
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data="stats"),
                InlineKeyboardButton("📅 Schedule", callback_data="schedule_menu")
            ],
            [InlineKeyboardButton("✅ Test Msg", callback_data="test_msg")]
        ]
        users = load_users()
        await update.message.reply_text(
            f"👑 *Admin Panel*\n\n👥 Members: *{len(users)}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = ""
    await update.message.reply_text("❌ Cancel ho gaya! /start likho.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if context.user_data.get("mode") == "broadcast_photo":
        photo = update.message.photo[-1].file_id
        caption = update.message.caption or "📢 FinalStrike Update!"
        users = load_users()
        sent = 0
        failed = 0
        for uid in users:
            try:
                await context.bot.send_photo(
                    chat_id=int(uid),
                    photo=photo,
                    caption=f"📢 *FinalStrike Update:*\n\n{caption}\n\n@FinalStrike02",
                    parse_mode="Markdown"
                )
                sent += 1
            except:
                failed += 1
        context.user_data["mode"] = ""
        await update.message.reply_text(
            f"✅ *Photo Broadcast Done!*\n✅ Bheja: {sent}\n❌ Failed: {failed}"
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ FinalStrike Broadcast Bot chal raha hai...")
    print("👥 Sab members ko message karo bina ek ek ko msg kiye!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

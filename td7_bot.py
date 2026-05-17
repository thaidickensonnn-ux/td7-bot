"""
TD7 Trading - Telegram Qualification Bot
=========================================
Qualifies leads from the free community and sends serious ones to @thaid7.

SETUP:
  pip install python-telegram-bot

HOW TO GET YOUR BOT TOKEN:
  1. Open Telegram, search @BotFather
  2. Send /newbot and follow the steps
  3. Copy the token it gives you and paste below

RUN:
  python td7_bot.py
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ─────────────────────────────────────────────
# CONFIG — paste your BotFather token here
# ─────────────────────────────────────────────
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8670540729:AAG46N_Tok4wXbWHRTfx2lRn6ZfBAFD_my0")

# ─────────────────────────────────────────────
# CONVERSATION STATES
# ─────────────────────────────────────────────
EXPERIENCE, BUDGET, EXPLAIN, NEXT_STEP, COLLECT_READY = range(5)

# ─────────────────────────────────────────────
# KEYBOARDS
# ─────────────────────────────────────────────
EXPERIENCE_KB = ReplyKeyboardMarkup(
    [["1", "2", "3"]],
    one_time_keyboard=True,
    resize_keyboard=True,
)

BUDGET_KB = ReplyKeyboardMarkup(
    [["1", "2", "3"], ["4", "5"]],
    one_time_keyboard=True,
    resize_keyboard=True,
)

NEXT_STEP_KB = ReplyKeyboardMarkup(
    [["1", "2"], ["3", "4"]],
    one_time_keyboard=True,
    resize_keyboard=True,
)

READY_KB = ReplyKeyboardMarkup(
    [["Yes", "No"]],
    one_time_keyboard=True,
    resize_keyboard=True,
)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
EXPERIENCE_MAP = {
    "1": "Beginner (never traded)",
    "2": "Learning (tried before)",
    "3": "Existing trader",
}

BUDGET_MAP = {
    "1": "£50",
    "2": "£100",
    "3": "£300",
    "4": "£500+",
    "5": "Not sure yet",
}

NEXT_STEP_MAP = {
    "1": "Join VIP",
    "2": "Help setting up",
    "3": "Free community first",
    "4": "Speak to Thai",
}

TRIGGER_WORDS = {"start", "ready", "vip", "help", "i want to start"}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def is_trigger(text: str) -> bool:
    return text.strip().lower() in TRIGGER_WORDS


# ─────────────────────────────────────────────
# CONVERSATION HANDLERS
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point — triggered by /start or trigger words."""
    await update.message.reply_text(
        "Perfect bro, I see you're ready to actually make a change.\n\n"
        "Before I help get you set up, I'm going to ask you a few quick "
        "questions so I know where you're at and what's best for you.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_text(
        "Have you ever traded before?\n\n"
        "1 — Never traded before\n"
        "2 — Tried it before but still learning\n"
        "3 — Yes, I already trade",
        reply_markup=EXPERIENCE_KB,
    )
    return EXPERIENCE


async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store experience level, ask about budget."""
    choice = update.message.text.strip()
    if choice not in EXPERIENCE_MAP:
        await update.message.reply_text(
            "Just tap 1, 2, or 3 below 👇",
            reply_markup=EXPERIENCE_KB,
        )
        return EXPERIENCE

    context.user_data["experience"] = EXPERIENCE_MAP[choice]

    await update.message.reply_text(
        "How much are you ready to start with?\n\n"
        "Minimum is £50.\n\n"
        "Most people start with around £300 because it gives more room "
        "to manage trades properly.\n\n"
        "1 — £50\n"
        "2 — £100\n"
        "3 — £300\n"
        "4 — £500+\n"
        "5 — Not sure yet",
        reply_markup=BUDGET_KB,
    )
    return BUDGET


async def budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store budget, explain how signals work."""
    choice = update.message.text.strip()
    if choice not in BUDGET_MAP:
        await update.message.reply_text(
            "Tap a number 1–5 below 👇",
            reply_markup=BUDGET_KB,
        )
        return BUDGET

    context.user_data["budget"] = BUDGET_MAP[choice]

    await update.message.reply_text(
        "Here's how it works 👇\n\n"
        "We send trading signals into the group.\n\n"
        "A signal tells you:\n\n"
        "• What pair to trade\n"
        "• Whether to buy or sell\n"
        "• Entry price\n"
        "• Stop loss\n"
        "• Take profit\n\n"
        "Example:\n\n"
        "BUY XAU/USD\n"
        "Entry: 4751\n"
        "Stop Loss: 4746\n"
        "Take Profit: 4772",
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_text(
        "What do you want help with?\n\n"
        "1 — Join VIP\n"
        "2 — Help setting up\n"
        "3 — Free community first\n"
        "4 — I want to speak to Thai",
        reply_markup=NEXT_STEP_KB,
    )
    return NEXT_STEP


async def next_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store goal, ask if ready today."""
    choice = update.message.text.strip()
    if choice not in NEXT_STEP_MAP:
        await update.message.reply_text(
            "Tap 1, 2, 3, or 4 below 👇",
            reply_markup=NEXT_STEP_KB,
        )
        return NEXT_STEP

    context.user_data["goal"] = NEXT_STEP_MAP[choice]

    await update.message.reply_text(
        "One last thing — are you ready to get started today?",
        reply_markup=READY_KB,
    )
    return COLLECT_READY


async def collect_ready(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect final answer, send summary, direct to @thaid7."""
    answer = update.message.text.strip().lower()
    if answer not in ("yes", "no"):
        await update.message.reply_text(
            "Just tap Yes or No 👇",
            reply_markup=READY_KB,
        )
        return COLLECT_READY

    context.user_data["ready_today"] = "Yes" if answer == "yes" else "No"

    ud = context.user_data
    experience_val = ud.get("experience", "Unknown")
    budget_val = ud.get("budget", "Unknown")
    goal_val = ud.get("goal", "Unknown")
    ready_val = ud.get("ready_today", "Unknown")

    # Determine if setup help is needed
    setup_help = "Yes" if goal_val == "Help setting up" else "No"

    await update.message.reply_text(
        f"Perfect bro.\n\n"
        f"Message Thai now:\n\n"
        f"👉 @thaid7\n\n"
        f"Send him this:\n\n"
        f"VIP READY\n\n"
        f"Starting amount: {budget_val}\n"
        f"Experience level: {experience_val}\n"
        f"Setup help: {setup_help}\n"
        f"Ready today: {ready_val}\n"
        f"Goal: {goal_val}",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Log the lead to the console so you can monitor
    logging.info(
        "LEAD | user=%s | budget=%s | exp=%s | setup=%s | ready=%s | goal=%s",
        update.effective_user.username or update.effective_user.id,
        budget_val,
        experience_val,
        setup_help,
        ready_val,
        goal_val,
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Allow user to cancel and restart."""
    await update.message.reply_text(
        "No worries. Message @thaid7 directly whenever you're ready.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def trigger_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle trigger words like READY, VIP, HELP, etc."""
    if is_trigger(update.message.text):
        return await start(update, context)
    return ConversationHandler.END


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                trigger_handler,
            ),
        ],
        states={
            EXPERIENCE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, experience)],
            BUDGET:        [MessageHandler(filters.TEXT & ~filters.COMMAND, budget)],
            NEXT_STEP:     [MessageHandler(filters.TEXT & ~filters.COMMAND, next_step)],
            COLLECT_READY: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_ready)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)

    print("✅ TD7 Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

from telegram import Update
from telegram.ext import ContextTypes
from bot.core.subscriptions import save_subscription, remove_subscription, get_subscription
from bot.core.utils import normalize_city_name

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sub [city] command"""
    if not context.args:
        await update.message.reply_text("❌ Please provide a city name, e.g.: `/sub London`", parse_mode="Markdown")
        return
    
    city = normalize_city_name(" ".join(context.args))
    save_subscription(update.effective_chat.id, city)
    await update.message.reply_text(
        f"✅ *Subscription active!*\n"
        f"I will send you a forecast for *{city}* every day at 7:00 AM.\n\n"
        f"To check your subscription: /mysub\n"
        f"To unsubscribe: /unsub", 
        parse_mode="Markdown"
    )

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unsub command"""
    if remove_subscription(update.effective_chat.id):
        await update.message.reply_text("🔕 Subscription has been cancelled. You will no longer receive daily updates.")
    else:
        await update.message.reply_text("ℹ️ You don't have an active subscription.")

async def my_subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mysub command"""
    city = get_subscription(update.effective_chat.id)
    if city:
        await update.message.reply_text(
            f"🔔 *Your Current Subscription*\n\n"
            f"📍 City: *{city}*\n"
            f"⏰ Time: Daily at 7:00 AM\n\n"
            f"To change city, use `/sub [New City]`.\n"
            f"To unsubscribe, use /unsub.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "ℹ️ *You are not subscribed to any daily forecasts.*\n\n"
            "To subscribe, type `/sub [City Name]`.",
            parse_mode="Markdown"
        )

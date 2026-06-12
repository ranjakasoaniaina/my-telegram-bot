# handlers/owner_stats.py

from telegram import Update
from telegram.ext import ContextTypes
from menu.stats.show_owner_stats import show_owner_stats


async def set_stats_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    period = query.data.split(":")[-1]  # "stats:period:weekly" → "weekly"
    context.user_data["stats_period"] = period
    await show_owner_stats(update, context)
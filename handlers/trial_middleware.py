# handlers/trial_middleware.py

from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from texts import t


async def trial_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None or update.effective_user.id != context.bot_data.get("owner_id"):
        return

    trial_key = "trial_end"
    if trial_key not in context.user_data:
        return

    trial_end_str = context.user_data[trial_key]
    try:
        trial_end_date = datetime.fromisoformat(trial_end_str).date()
    except ValueError:
        return

    if datetime.now().date() > trial_end_date:
        lang = context.user_data.get("lang", "fr")
        texte = t("trial_expired", lang)
        if update.message:
            await update.message.reply_text(texte)
        elif update.callback_query:
            await update.callback_query.answer()
            try:
                await update.callback_query.edit_message_text(texte)
            except Exception:
                pass
        # Pas de raise StopPropagation – le simple fait de répondre suffit à bloquer la suite
        return
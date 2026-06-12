# menu/reminders/show_reminder_enter_recurrence.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message


async def show_reminder_enter_recurrence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le choix de la récurrence (création ou modification)."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")
    draft = context.user_data.get("reminder_draft", {})
    current = draft.get("recurrence")

    # Correspondance entre la clé interne et le chemin de traduction
    recurrence_keys = {
        "once": "reminder_recurrence_once",
        "daily": "reminder_recurrence_daily",
        "weekly": "reminder_recurrence_weekly",
        "monthly": "reminder_recurrence_monthly",
    }

    if current:
        current_label = t(recurrence_keys.get(current, "reminder_recurrence_daily"), lang)
        texte = t("reminder_edit_recurrence_prompt", lang, current=current_label)
        boutons = [
            [InlineKeyboardButton(t("reminder_recurrence_once", lang), callback_data="reminder:recurrence:once")],
            [InlineKeyboardButton(t("reminder_recurrence_daily", lang), callback_data="reminder:recurrence:daily")],
            [InlineKeyboardButton(t("reminder_recurrence_weekly", lang), callback_data="reminder:recurrence:weekly")],
            [InlineKeyboardButton(t("reminder_recurrence_monthly", lang), callback_data="reminder:recurrence:monthly")],
            [InlineKeyboardButton(t("keep_current", lang), callback_data="reminder:skip_recurrence")],
            [InlineKeyboardButton(t("back", lang), callback_data="nav:back")]
        ]
    else:
        texte = t("reminder_recurrence_prompt", lang)
        boutons = [
            [InlineKeyboardButton(t("reminder_recurrence_once", lang), callback_data="reminder:recurrence:once")],
            [InlineKeyboardButton(t("reminder_recurrence_daily", lang), callback_data="reminder:recurrence:daily")],
            [InlineKeyboardButton(t("reminder_recurrence_weekly", lang), callback_data="reminder:recurrence:weekly")],
            [InlineKeyboardButton(t("reminder_recurrence_monthly", lang), callback_data="reminder:recurrence:monthly")],
            [InlineKeyboardButton(t("back", lang), callback_data="nav:back")]
        ]

    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "reminder_enter_recurrence"
    if context.user_data.get("reminder_edit_id"):
        context.user_data["step_parent"] = "reminder_enter_datetime"
    else:
        context.user_data["step_parent"] = "reminder_enter_datetime"
    context.user_data["menu_parent"] = "main"

    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)
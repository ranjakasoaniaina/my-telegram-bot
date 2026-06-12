# menu/reminders/show_reminder_enter_text.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message


async def show_reminder_enter_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche l'écran de saisie du texte (création ou modification)."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")
    draft = context.user_data.get("reminder_draft", {})
    current = draft.get("text")

    if current:
        texte = t("reminder_edit_text_prompt", lang, current=current)
        boutons = [
            [InlineKeyboardButton(t("keep_current", lang), callback_data="reminder:skip_text")],
            [InlineKeyboardButton(t("cancel", lang), callback_data="nav:back")]
        ]
    else:
        texte = t("reminder_text_prompt", lang)
        boutons = [
            [InlineKeyboardButton(t("cancel", lang), callback_data="nav:back")]
        ]

    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "reminder_enter_text"
    if context.user_data.get("reminder_edit_id"):
        context.user_data["step_parent"] = "reminder_enter_recurrence"
    else:
        context.user_data["step_parent"] = "reminder_enter_recurrence"
    context.user_data["menu_parent"] = "main"

    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)
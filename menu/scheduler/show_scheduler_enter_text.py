# menu/scheduler/show_scheduler_enter_text.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message

async def show_scheduler_enter_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche l'écran de saisie du texte (création ou modification pré-remplie)."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")
    draft = context.user_data.get("scheduler_draft", {})
    current = draft.get("text")

    if current:
        texte = t("scheduler_edit_text_prompt", lang, current=current)
        boutons = [
            [InlineKeyboardButton(t("keep_current", lang), callback_data="scheduler:skip_text")],
            [InlineKeyboardButton(t("cancel", lang), callback_data="nav:back")]
        ]
    else:
        texte = t("scheduler_create_text_prompt", lang)
        boutons = [
            [InlineKeyboardButton(t("cancel", lang), callback_data="nav:back")]
        ]

    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "scheduler_enter_text"
    context.user_data["step_parent"] = "scheduler_select_groups" if not current else "scheduler_edit_list"
    context.user_data["menu_parent"] = "scheduler_main"

    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)
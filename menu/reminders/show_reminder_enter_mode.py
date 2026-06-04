# menu/reminders/show_reminder_enter_mode.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message


async def show_reminder_enter_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le choix du mode d'envoi du rappel (privé ou groupes)."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")
    # Réinitialiser les données temporaires pour un nouveau rappel
    context.user_data["reminder_mode"] = None
    context.user_data["reminder_draft"] = {}
    context.user_data["reminder_selected_group_ids"] = []
    
    texte = t("reminder_mode_prompt", lang)

    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("reminder_mode_private", lang), callback_data="reminder:mode:private")],
        [InlineKeyboardButton(t("reminder_mode_groups", lang), callback_data="reminder:mode:groups")],
        [InlineKeyboardButton(t("back", lang), callback_data="nav:back")]
    ])

    context.user_data["current_screen"] = "reminder_enter_mode"
    context.user_data["step_parent"] = "reminder_main"
    context.user_data["menu_parent"] = "main"

    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)
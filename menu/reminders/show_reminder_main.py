# menu/reminders/show_reminder_main.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t


async def show_reminder_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le menu principal des rappels."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")

    # --- Message de succès temporaire (création, modification, suppression) ---
    success_msg = ""
    key = context.user_data.pop("action_success_msg_key", None)
    if key:
        success_msg = t(key, lang) + "\n\n"

    texte = success_msg + t("reminder_main_title", lang)

    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("reminder_main_create", lang), callback_data="reminder:new")],
        [InlineKeyboardButton(t("reminder_main_edit", lang), callback_data="reminder:edit_list")],
        [InlineKeyboardButton(t("reminder_main_delete", lang), callback_data="reminder:delete_list")],
        [InlineKeyboardButton(t("back", lang), callback_data="nav:back")]
    ])

    context.user_data["current_screen"] = "reminder_main"
    context.user_data["step_parent"] = None
    context.user_data["menu_parent"] = "main"

    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)
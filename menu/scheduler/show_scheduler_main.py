# menu/scheduler/show_scheduler_main.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message



async def show_scheduler_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le menu principal des messages programmés."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")

    # --- Message de succès temporaire (création, modification, suppression) ---
    success_msg = ""
    key = context.user_data.pop("action_success_msg_key", None)
    if key:
        success_msg = t(key, lang) + "\n\n"

    # --- Texte du menu ---
    texte = success_msg + t("scheduler_main_title", lang)

    # --- Clavier ---
    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("scheduler_main_create", lang), callback_data="scheduler:new")],
        [InlineKeyboardButton(t("scheduler_main_edit", lang), callback_data="scheduler:edit_list")],
        [InlineKeyboardButton(t("scheduler_main_delete", lang), callback_data="scheduler:delete_list")],
        [InlineKeyboardButton(t("back", lang), callback_data="nav:back")]
    ])

    # --- Navigation ---
    context.user_data["current_screen"] = "scheduler_main"
    context.user_data["step_parent"] = None
    context.user_data["menu_parent"] = "main"

    # --- Affichage (édition ou envoi) ---
    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        chat_id = update.effective_chat.id
        message_id = context.user_data.get("active_message_id")
        if message_id:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=texte,
                    reply_markup=clavier
                )
            except Exception:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                except Exception:
                    pass
                message = await context.bot.send_message(chat_id=chat_id, text=texte, reply_markup=clavier)
                context.user_data["active_message_id"] = message.message_id
        else:
            message = await context.bot.send_message(chat_id=chat_id, text=texte, reply_markup=clavier)
            context.user_data["active_message_id"] = message.message_id
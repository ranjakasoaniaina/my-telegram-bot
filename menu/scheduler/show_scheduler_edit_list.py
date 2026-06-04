# menu/scheduler/show_scheduler_edit_list.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message



async def show_scheduler_edit_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche la liste des messages programmés pour modification (sélection simple)."""
    query = update.callback_query
    if query:
        await query.answer()

    user_id = str(update.effective_user.id)
    lang = context.user_data.get("lang", "fr")
    persistent = context.bot_data.get("persistent", {})
    user_pdata = persistent.get(user_id, {})
    messages = user_pdata.get("scheduled_messages", [])

    if messages:
        texte = t("scheduler_edit_list_title", lang)
        boutons = []
        for msg in messages:
            text_preview = msg.get("text", "???")
            if len(text_preview) > 55:
                text_preview = text_preview[:55] + "…"
            interval = msg.get("interval_minutes", 0)
            sent = msg.get("sent_count", 0)
            max_sends = msg.get("max_sends", 0)
            group_count = len(msg.get("group_ids", []))
            resume = t("scheduler_edit_item_summary", lang,
                       text=text_preview,
                       interval=interval,
                       sent=sent,
                       max_sends=max_sends,
                       group_count=group_count)

            boutons.append([
                InlineKeyboardButton(
                    resume,
                    callback_data=f"scheduler:select:{msg['id']}"
                )
            ])
    else:
        texte = t("scheduler_edit_list_empty", lang)
        boutons = []

    # Ligne de navigation
    boutons.append([
        InlineKeyboardButton(t("back", lang), callback_data="nav:back")
    ])

    clavier = InlineKeyboardMarkup(boutons)

    # Mise à jour de la navigation
    context.user_data["current_screen"] = "scheduler_edit_list"
    context.user_data["step_parent"] = "scheduler_main"
    context.user_data["menu_parent"] = "main"

    # Affichage (édition ou envoi)
    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)
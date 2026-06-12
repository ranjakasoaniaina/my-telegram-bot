# menu/scheduler/show_scheduler_confirm.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message



async def show_scheduler_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le récapitulatif et demande confirmation avant enregistrement (création ou modification)."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")
    draft = context.user_data.get("scheduler_draft", {})
    selected_ids = context.user_data.get("scheduler_selected_group_ids", [])

    # Données pour le résumé
    full_text = draft.get("text", "???")
    display_text = full_text if len(full_text) <= 80 else full_text[:80] + "…"
    interval = draft.get("interval", 0)
    count = draft.get("count", 0)
    count_groups = len(selected_ids)

    # Récapitulatif localisé
    destination = t("scheduler_confirm_destination", lang, count=count_groups)
    texte = t("scheduler_confirm_text", lang,
              destination=destination,
              text=display_text,
              interval=interval,
              count=count)

    # Bouton de confirmation adapté au contexte
    if context.user_data.get("scheduler_edit_msg_id"):
        callback_confirm = "scheduler:confirm_edit"
        label_confirm = t("scheduler_confirm_edit_button", lang)
    else:
        callback_confirm = "scheduler:confirm_create"
        label_confirm = t("scheduler_confirm_create_button", lang)

    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(label_confirm, callback_data=callback_confirm)],
        [InlineKeyboardButton(t("back", lang), callback_data="nav:back")]
    ])

    # Navigation
    context.user_data["current_screen"] = "scheduler_confirm"
    context.user_data["step_parent"] = "scheduler_enter_count"
    context.user_data["menu_parent"] = "main"

    # Affichage (édition ou envoi)
    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)
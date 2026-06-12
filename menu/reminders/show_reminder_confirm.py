# menu/reminders/show_reminder_confirm.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message


async def show_reminder_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le récapitulatif du rappel avant enregistrement (création ou modification)."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")
    draft = context.user_data.get("reminder_draft", {})
    mode = context.user_data.get("reminder_mode", "private")
    selected_ids = context.user_data.get("reminder_selected_group_ids", [])

    # Récupération des infos
    date_str = draft.get("datetime", "???")
    recurrence = draft.get("recurrence", "")
    # Libellé localisé de la récurrence
    rec_keys = {
        "once": "reminder_recurrence_once",
        "daily": "reminder_recurrence_daily",
        "weekly": "reminder_recurrence_weekly",
        "monthly": "reminder_recurrence_monthly",
    }
    recurrence_label = t(rec_keys.get(recurrence, "reminder_recurrence_daily"), lang)
    text_msg = draft.get("text", "???")

    # Destination localisée
    if mode == "groups":
        count = len(selected_ids)
        dest = t("reminder_dest_groups", lang, count=count)
    else:
        dest = t("reminder_dest_private", lang)

    texte = t("reminder_confirm_text", lang,
              dest=dest,
              text=text_msg,
              datetime=date_str,
              recurrence=recurrence_label)

    # Bouton de confirmation adapté au contexte
    if context.user_data.get("reminder_edit_id"):
        callback_confirm = "reminder:confirm_edit"
        label_confirm = t("reminder_confirm_edit_button", lang)
    else:
        callback_confirm = "reminder:confirm_create"
        label_confirm = t("reminder_confirm_create_button", lang)

    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(label_confirm, callback_data=callback_confirm)],
        [InlineKeyboardButton(t("back", lang), callback_data="nav:back")]
    ])

    # Navigation
    context.user_data["current_screen"] = "reminder_confirm"
    context.user_data["step_parent"] = "reminder_enter_text"
    context.user_data["menu_parent"] = "main"

    # Affichage (édition ou envoi)
    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)
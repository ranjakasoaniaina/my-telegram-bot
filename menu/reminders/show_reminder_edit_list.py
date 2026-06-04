# menu/reminders/show_reminder_edit_list.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message


async def show_reminder_edit_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche la liste des rappels existants pour modification (sélection simple)."""
    query = update.callback_query
    if query:
        await query.answer()

    user_id = str(update.effective_user.id)
    lang = context.user_data.get("lang", "fr")
    persistent = context.bot_data.get("persistent", {})
    user_pdata = persistent.get(user_id, {})
    reminders = user_pdata.get("reminders", [])

    # Correspondances pour les récurrences courtes
    short_rec_map = {
        "once": "reminder_recurrence_short_once",
        "daily": "reminder_recurrence_short_daily",
        "weekly": "reminder_recurrence_short_weekly",
        "monthly": "reminder_recurrence_short_monthly",
    }

    if reminders:
        texte = t("reminder_edit_list_title", lang)
        boutons = []
        for rem in reminders:
            # Résumé texte
            text_preview = rem.get("text", "???")
            if len(text_preview) > 45:
                text_preview = text_preview[:45] + "…"

            # Récurrence (version courte)
            recurrence = rem.get("recurrence", "")
            rec_key = short_rec_map.get(recurrence, "reminder_recurrence_short_daily")
            rec_label = t(rec_key, lang)

            # Date
            date_str = rem.get("datetime", "???")

            # Destination
            mode = rem.get("mode", "private")
            if mode == "groups":
                nb = len(rem.get("group_ids", []))
                dest = t("reminder_dest_groups", lang, count=nb)
            else:
                dest = t("reminder_dest_private", lang)

            resume = f"{text_preview} ({rec_label}, {date_str}, {dest})"

            boutons.append([
                InlineKeyboardButton(
                    resume,
                    callback_data=f"reminder:select:{rem['id']}"
                )
            ])
    else:
        texte = t("reminder_edit_list_empty", lang)
        boutons = []

    boutons.append([
        InlineKeyboardButton(t("back", lang), callback_data="nav:back")
    ])

    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "reminder_edit_list"
    context.user_data["step_parent"] = "reminder_main"
    context.user_data["menu_parent"] = "main"

    # Affichage (édition ou envoi)
    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)
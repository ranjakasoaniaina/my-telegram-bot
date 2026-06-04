# menu/reminders/show_reminder_delete_list.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message


async def show_reminder_delete_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche la liste des rappels avec toggles pour suppression multiple."""
    query = update.callback_query
    if query:
        await query.answer()

    user_id = str(update.effective_user.id)
    lang = context.user_data.get("lang", "fr")
    persistent = context.bot_data.get("persistent", {})
    user_pdata = persistent.get(user_id, {})
    reminders = user_pdata.get("reminders", [])
    delete_ids = context.user_data.get("reminder_delete_ids", [])

    # Correspondances pour les récurrences courtes
    short_rec_map = {
        "once": "reminder_recurrence_short_once",
        "daily": "reminder_recurrence_short_daily",
        "weekly": "reminder_recurrence_short_weekly",
        "monthly": "reminder_recurrence_short_monthly",
    }

    if reminders:
        texte = t("reminder_delete_list_title", lang)
        boutons = []
        for rem in reminders:
            text_preview = rem.get("text", "???")
            if len(text_preview) > 45:
                text_preview = text_preview[:45] + "…"

            recurrence = rem.get("recurrence", "")
            rec_key = short_rec_map.get(recurrence, "reminder_recurrence_short_daily")
            rec_label = t(rec_key, lang)

            date_str = rem.get("datetime", "???")

            mode = rem.get("mode", "private")
            if mode == "groups":
                nb = len(rem.get("group_ids", []))
                dest = t("reminder_dest_groups", lang, count=nb)
            else:
                dest = t("reminder_dest_private", lang)

            resume = t("reminder_delete_item_summary", lang,
                       text=text_preview,
                       rec=rec_label,
                       date=date_str,
                       dest=dest)

            prefix = "☑" if rem["id"] in delete_ids else "☐"
            boutons.append([
                InlineKeyboardButton(
                    f"{prefix} {resume}",
                    callback_data=f"reminder:delete_toggle:{rem['id']}"
                )
            ])

        # Ligne Tout sélectionner / Tout désélectionner
        boutons.append([
            InlineKeyboardButton(t("select_all", lang), callback_data="reminder:delete_select_all"),
            InlineKeyboardButton(t("deselect_all", lang), callback_data="reminder:delete_deselect_all"),
        ])

        # Bouton "Supprimer la sélection" uniquement si au moins un coché
        if delete_ids:
            count = len(delete_ids)
            boutons.append([
                InlineKeyboardButton(
                    t("delete_selected_button", lang, count=count),
                    callback_data="reminder:delete_confirm"
                )
            ])
    else:
        texte = t("reminder_delete_list_empty", lang)
        boutons = []

    # Retour
    boutons.append([
        InlineKeyboardButton(t("back", lang), callback_data="nav:back")
    ])

    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "reminder_delete_list"
    context.user_data["step_parent"] = "reminder_main"
    context.user_data["menu_parent"] = "main"

    # Affichage (édition ou envoi)
    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)
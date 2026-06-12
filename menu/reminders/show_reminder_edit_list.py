# menu/reminders/show_reminder_edit_list.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message, estimate_width, pad_to_width
from config import MAX_MESSAGE_PREVIEW_LENGTH


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

        # --- Génération unique des résumés ---
        resumes = []
        for rem in reminders:
            text_preview = rem.get("text", "???")
            if len(text_preview) > MAX_MESSAGE_PREVIEW_LENGTH:
                text_preview = text_preview[:MAX_MESSAGE_PREVIEW_LENGTH] + "…"
            rec_key = short_rec_map.get(rem.get("recurrence", ""), "reminder_recurrence_short_daily")
            rec_label = t(rec_key, lang)
            date_str = rem.get("datetime", "???")
            mode = rem.get("mode", "private")
            if mode == "groups":
                nb = len(rem.get("group_ids", []))
                dest = t("reminder_dest_groups", lang, count=nb)
            else:
                dest = t("reminder_dest_private", lang)
            resume = f"{text_preview} ({rec_label}, {date_str}, {dest})"
            resumes.append(resume)

        # --- Alignement ---
        widths = [estimate_width(r) for r in resumes]
        target = max(widths) if widths else 0
        padded_resumes = [pad_to_width(r, target) for r in resumes]

        # --- Création des boutons ---
        boutons = []
        for i, rem in enumerate(reminders):
            boutons.append([
                InlineKeyboardButton(padded_resumes[i], callback_data=f"reminder:select:{rem['id']}")
            ])
    else:
        texte = t("reminder_edit_list_empty", lang)
        boutons = []

    # Bouton Retour
    boutons.append([
        InlineKeyboardButton(t("back", lang), callback_data="nav:back")
    ])

    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "reminder_edit_list"
    context.user_data["step_parent"] = "reminder_main"
    context.user_data["menu_parent"] = "main"

    # Affichage (délégation complète)
    await display_message(update, context, texte, clavier)
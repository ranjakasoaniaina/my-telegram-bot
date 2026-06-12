# menu/scheduler/show_scheduler_edit_list.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message, estimate_width, pad_to_width
from config import MAX_MESSAGE_PREVIEW_LENGTH


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

        # --- Génération unique des résumés ---
        resumes = []
        for msg in messages:
            text_preview = msg.get("text", "???")
            if len(text_preview) > MAX_MESSAGE_PREVIEW_LENGTH:
                text_preview = text_preview[:MAX_MESSAGE_PREVIEW_LENGTH] + "…"
            interval = msg.get("interval_minutes", 0)
            sent = msg.get("sent_count", 0)
            max_sends = msg.get("max_sends", 0)
            group_count = len(msg.get("group_ids", []))
            resume = t("scheduler_edit_item_summary", lang,
                       text=text_preview, interval=interval, sent=sent,
                       max_sends=max_sends, group_count=group_count)
            resumes.append(resume)

        # --- Alignement ---
        widths = [estimate_width(r) for r in resumes]
        target = max(widths) if widths else 0
        padded_resumes = [pad_to_width(r, target) for r in resumes]

        # --- Création des boutons ---
        boutons = []
        for i, msg in enumerate(messages):
            boutons.append([
                InlineKeyboardButton(
                    padded_resumes[i],
                    callback_data=f"scheduler:select:{msg['id']}"
                )
            ])
    else:
        texte = t("scheduler_edit_list_empty", lang)
        boutons = []

    # Retour
    boutons.append([
        InlineKeyboardButton(t("back", lang), callback_data="nav:back")
    ])

    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "scheduler_edit_list"
    context.user_data["step_parent"] = "scheduler_main"
    context.user_data["menu_parent"] = "main"

    await display_message(update, context, texte, clavier)
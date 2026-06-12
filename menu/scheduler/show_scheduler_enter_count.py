# menu/scheduler/show_scheduler_enter_count.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message



async def show_scheduler_enter_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche l'écran de saisie du nombre d'envois (création ou modification)."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")
    error_msg = context.user_data.pop("show_error_msg", None)
    draft = context.user_data.get("scheduler_draft", {})
    current = draft.get("count")

    if current:
        texte = t("scheduler_edit_count_prompt", lang, current=current)
        boutons = [
            [InlineKeyboardButton(t("keep_current", lang), callback_data="scheduler:skip_count")],
            [InlineKeyboardButton(t("cancel", lang), callback_data="nav:back")]
        ]
    else:
        texte = t("scheduler_create_count_prompt", lang)
        boutons = [
            [InlineKeyboardButton(t("cancel", lang), callback_data="nav:back")]
        ]

    # Afficher l'erreur de validation si présente
    if error_msg:
        texte = f"❌ {error_msg}\n\n{texte}"

    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "scheduler_enter_count"
    context.user_data["step_parent"] = "scheduler_enter_interval"
    context.user_data["menu_parent"] = "scheduler_main"

    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)
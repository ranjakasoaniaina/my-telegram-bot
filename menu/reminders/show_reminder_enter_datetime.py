# menu/reminders/show_reminder_enter_datetime.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message


async def show_reminder_enter_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche l'écran de saisie de la date/heure (création ou modification)."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")
    error_msg = context.user_data.pop("show_error_msg", None)
    draft = context.user_data.get("reminder_draft", {})
    current = draft.get("datetime")

    if current:
        texte = t("reminder_edit_datetime_prompt", lang, current=current)
        boutons = [
            [InlineKeyboardButton(t("keep_current", lang), callback_data="reminder:skip_datetime")],
            [InlineKeyboardButton(t("cancel", lang), callback_data="nav:back")]
        ]
    else:
        texte = t("reminder_datetime_prompt", lang)
        boutons = [
            [InlineKeyboardButton(t("cancel", lang), callback_data="nav:back")]
        ]

    if error_msg:
        texte = f"❌ {error_msg}\n\n{texte}"

    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "reminder_enter_datetime"
    # step_parent déjà défini par l'appelant
    if not current:
        mode = context.user_data.get("reminder_mode", "private")
        if mode == "groups":
            context.user_data["step_parent"] = "reminder_select_groups"
        else:
            context.user_data["step_parent"] = "reminder_enter_mode"
    if context.user_data.get("reminder_edit_id"):
        context.user_data["step_parent"] = "reminder_edit_list"

    context.user_data["menu_parent"] = "main"

    await display_message(update, context, texte, clavier)
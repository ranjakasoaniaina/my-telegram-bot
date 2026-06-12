# menu/scheduler/show_scheduler_main.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message, estimate_width, pad_to_width


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

    texte = success_msg + t("scheduler_main_title", lang)

    # --- Boutons alignés (➕, ✍️, 🗑️) ---
    labels = [
        t("scheduler_main_create", lang),
        t("scheduler_main_edit", lang),
        t("scheduler_main_delete", lang),
    ]
    widths = [estimate_width(l) for l in labels]
    target = max(widths) if widths else 0
    padded = [pad_to_width(l, target) for l in labels]

    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(padded[0], callback_data="scheduler:new")],
        [InlineKeyboardButton(padded[1], callback_data="scheduler:edit_list")],
        [InlineKeyboardButton(padded[2], callback_data="scheduler:delete_list")],
        [InlineKeyboardButton(t("back", lang), callback_data="nav:back")]
    ])

    # --- Navigation ---
    context.user_data["current_screen"] = "scheduler_main"
    context.user_data["step_parent"] = None
    context.user_data["menu_parent"] = "main"

    # --- Affichage délégué ---
    await display_message(update, context, texte, clavier)
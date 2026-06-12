# menu/reminders/show_reminder_enter_mode.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message, estimate_width, pad_to_width


async def show_reminder_enter_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le choix du mode d'envoi du rappel (privé ou groupes)."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")

    # Réinitialiser les données temporaires pour un nouveau rappel
    context.user_data["reminder_mode"] = None
    context.user_data["reminder_draft"] = {}
    context.user_data["reminder_selected_group_ids"] = []

    texte = t("reminder_mode_prompt", lang)

    # --- Boutons alignés (mode privé et groupes) ---
    labels = [
        t("reminder_mode_private", lang),
        t("reminder_mode_groups", lang),
    ]
    widths = [estimate_width(l) for l in labels]
    target = max(widths) if widths else 0
    padded = [pad_to_width(l, target) for l in labels]

    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(padded[0], callback_data="reminder:mode:private")],
        [InlineKeyboardButton(padded[1], callback_data="reminder:mode:groups")],
        [InlineKeyboardButton(t("back", lang), callback_data="nav:back")]
    ])

    context.user_data["current_screen"] = "reminder_enter_mode"
    context.user_data["step_parent"] = "reminder_main"
    context.user_data["menu_parent"] = "main"

    # Délégation de l’affichage à display_message (gère édition ou envoi)
    await display_message(update, context, texte, clavier)
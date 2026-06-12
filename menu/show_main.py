# menu/show_main.py

from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import OWNER_ID, TRIAL_DAYS
from texts import t
from menu.display_utils import display_message, estimate_width, pad_to_width


async def show_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le menu principal (réservé au client propriétaire)."""
    
    # Seul le client (OWNER_ID) peut voir ce menu
    if update.effective_user.id != OWNER_ID:
        return

    # Détection de la langue
    detected = update.effective_user.language_code or "en"
    context.user_data["lang"] = "fr" if detected.startswith("fr") else "en"
    lang = context.user_data["lang"]

    # Gestion de l'essai
    trial_key = "trial_end"
    first_start = (trial_key not in context.user_data)
    now = datetime.now()

    if first_start:
        end_date = now + timedelta(days=TRIAL_DAYS)
        context.user_data[trial_key] = end_date.isoformat()

        if lang == "fr":
            end_date_str = end_date.strftime("%d/%m/%Y")
        else:
            end_date_str = end_date.strftime("%m/%d/%Y")

        activation_text = t("trial_started", lang, days=TRIAL_DAYS, end_date=end_date_str)
        if update.message:
            await update.message.reply_text(activation_text)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=activation_text)

    # Texte du menu
    if first_start:
        texte = t("menu_prompt", lang)
    else:
        texte = t("main_menu_welcome", lang)

    # Boutons alignés (Groupes, Envois, Rappels)
    labels = [
        t("main_menu_group_mgmt", lang),
        t("main_menu_scheduled", lang),
        t("main_menu_reminders", lang),
    ]
    widths = [estimate_width(l) for l in labels]
    target_width = max(widths)
    padded_labels = [pad_to_width(l, target_width) for l in labels]

    boutons = [
        [InlineKeyboardButton(padded_labels[0], callback_data="menu:group_config_choice")],
        [InlineKeyboardButton(padded_labels[1], callback_data="menu:scheduler")],
        [InlineKeyboardButton(padded_labels[2], callback_data="menu:reminders")],
    ]
    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "main"
    context.user_data["step_parent"] = None
    context.user_data["menu_parent"] = None

    await display_message(update, context, texte, clavier)
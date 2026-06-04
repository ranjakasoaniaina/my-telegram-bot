# menu/groups/welcome.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from storage import save_data
from texts import t
from menu.display_utils import display_message


async def show_welcome_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche la configuration du message de bienvenue (handler d'entrée + édition après saisie)."""
    query = update.callback_query
    if query:
        await query.answer()

    user_id = str(update.effective_user.id)
    group_id = str(context.user_data.get("selected_group_id"))
    group_title = context.user_data.get("selected_group_title", "Groupe inconnu")
    lang = context.user_data.get("lang", "fr")

    # Récupération / création de la config persistante
    persistent = context.bot_data.setdefault("persistent", {})
    user_pdata = persistent.setdefault(user_id, {})
    welcome_config = user_pdata.setdefault("welcome_config", {})

    if group_id not in welcome_config:
        welcome_config[group_id] = {"enabled": False, "message": "Bienvenue {username} !"}
        await save_data(context)

    enabled = welcome_config[group_id]["enabled"]
    message = welcome_config[group_id]["message"]

    success_msg = ""
    if "action_success_msg" in context.user_data:
        success_msg = context.user_data.pop("action_success_msg") + "\n\n"

    status_text = t("welcome_status_enabled", lang) if enabled else t("welcome_status_disabled", lang)
    texte = (
        success_msg
        + t("welcome_config_title", lang, group=group_title)
        + "\n"
        + t("welcome_current_message", lang, status=status_text, message=message)
    )

    boutons = []
    if enabled:
        boutons.append([InlineKeyboardButton(t("deactivate", lang), callback_data="welcome:toggle")])
        boutons.append([InlineKeyboardButton(t("welcome_edit_button", lang), callback_data="welcome:edit_message")])
    else:
        boutons.append([InlineKeyboardButton(t("activate", lang), callback_data="welcome:toggle")])
    boutons.append([InlineKeyboardButton(t("back", lang), callback_data="nav:back")])

    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "welcome_config"
    context.user_data["step_parent"] = "group_list"
    context.user_data["menu_parent"] = "main"

    # Affichage : édition du message actif ou envoi initial
    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)


async def show_welcome_edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche l'écran de saisie du nouveau message de bienvenue."""
    query = update.callback_query
    await query.answer()

    group_title = context.user_data.get("selected_group_title", "Groupe inconnu")
    lang = context.user_data.get("lang", "fr")

    texte = t("welcome_edit_prompt", lang, group=group_title)

    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("cancel", lang), callback_data="nav:back")]
    ])

    context.user_data["current_screen"] = "welcome_edit_message"
    context.user_data["step_parent"] = "welcome_config"
    context.user_data["menu_parent"] = "main"

    await query.edit_message_text(text=texte, reply_markup=clavier)
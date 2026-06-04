# menu/groups/antispam.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from storage import save_data
from texts import t
from menu.display_utils import display_message


async def show_antispam_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche la configuration Anti-spam (handler d'entrée + édition après saisie éventuelle)."""
    query = update.callback_query
    if query:
        await query.answer()

    user_id = str(update.effective_user.id)
    group_id = str(context.user_data.get("selected_group_id"))
    group_title = context.user_data.get("selected_group_title", "Groupe inconnu")
    lang = context.user_data.get("lang", "fr")

    persistent = context.bot_data.setdefault("persistent", {})
    user_pdata = persistent.setdefault(user_id, {})
    antispam_config = user_pdata.setdefault("antispam_config", {})

    if group_id not in antispam_config:
        antispam_config[group_id] = {
            "enabled": False,
            "block_links": True,
            "block_repeated": False
        }
        await save_data(context)

    config = antispam_config[group_id]
    enabled = config["enabled"]
    block_links = config.get("block_links", True)
    block_repeated = config.get("block_repeated", False)

    status = t("antispam_status_enabled", lang) if enabled else t("antispam_status_disabled", lang)
    texte = (
        t("antispam_config_title", lang, group=group_title) + "\n"
        + t("status_label", lang) + " " + status
    )

    if enabled:
        links_label = f"{t('antispam_block_links', lang)} : {'ON' if block_links else 'OFF'}"
        repeated_label = f"{t('antispam_block_repeated', lang)} : {'ON' if block_repeated else 'OFF'}"
        boutons = [
            [InlineKeyboardButton(links_label, callback_data="antispam:block_links")],
            [InlineKeyboardButton(repeated_label, callback_data="antispam:block_repeated")],
            [
                InlineKeyboardButton(t("deactivate", lang), callback_data="antispam:toggle"),
                InlineKeyboardButton(t("back", lang), callback_data="nav:back")
            ]
        ]
    else:
        boutons = [
            [
                InlineKeyboardButton(t("activate", lang), callback_data="antispam:toggle"),
                InlineKeyboardButton(t("back", lang), callback_data="nav:back")
            ]
        ]

    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "antispam_config"
    context.user_data["step_parent"] = "group_list"
    context.user_data["menu_parent"] = "main"

    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)
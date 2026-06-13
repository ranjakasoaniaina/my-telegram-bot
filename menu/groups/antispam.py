# menu/groups/antispam.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from storage import save_data
from texts import t
from menu.display_utils import display_message, estimate_width, pad_to_width


async def show_antispam_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche la configuration Anti-spam."""
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

    boutons = []

    if enabled:
        # 1. Textes de base (sans indicateur ON/OFF)
        base_links = t("antispam_block_links", lang)
        base_repeated = t("antispam_block_repeated", lang)

        # 2. Padder les textes de base à la même largeur
        bases = [base_links, base_repeated]
        widths_base = [estimate_width(b) for b in bases]
        target_base = max(widths_base) if widths_base else 0
        padded_links = pad_to_width(base_links, target_base)
        padded_repeated = pad_to_width(base_repeated, target_base)

        # 3. Padder les indicateurs ON/OFF pour qu'ils aient la même largeur
        on_text =  "ON"
        off_text = "OFF"
        indicator_widths = [estimate_width(on_text), estimate_width(off_text)]
        target_indicator = max(indicator_widths) if indicator_widths else 0
        padded_on = pad_to_width(on_text, target_indicator)
        padded_off = pad_to_width(off_text, target_indicator)

        # 4. Construire les labels complets
        label_links = f"{padded_links} : {padded_on if block_links else padded_off}"
        label_repeated = f"{padded_repeated} : {padded_on if block_repeated else padded_off}"

        boutons.append([InlineKeyboardButton(label_links, callback_data="antispam:block_links")])
        boutons.append([InlineKeyboardButton(label_repeated, callback_data="antispam:block_repeated")])
        boutons.append([
            InlineKeyboardButton(t("deactivate", lang), callback_data="antispam:toggle"),
            InlineKeyboardButton(t("back", lang), callback_data="nav:back")
        ])
    else:
        boutons.append([
            InlineKeyboardButton(t("activate", lang), callback_data="antispam:toggle"),
            InlineKeyboardButton(t("back", lang), callback_data="nav:back")
        ])

    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "antispam_config"
    context.user_data["step_parent"] = "group_list"
    context.user_data["menu_parent"] = "main"

    await display_message(update, context, texte, clavier)
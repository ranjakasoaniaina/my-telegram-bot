# handlers/group_manage/toggle.py

from telegram import Update
from telegram.ext import ContextTypes

from storage import save_data

from menu.groups.welcome  import show_welcome_config
from menu.groups.antispam import show_antispam_config

from menu.show_main import show_main   # pour le fallback de sécurité


async def toggle_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Active ou désactive le message de bienvenue pour le groupe sélectionné."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    group_id = context.user_data.get("selected_group_id")
    if group_id is None:
        await show_main(update, context)
        return

    group_id = str(group_id)
    persistent = context.bot_data.setdefault("persistent", {})
    user_pdata = persistent.setdefault(user_id, {})
    welcome_config = user_pdata.setdefault("welcome_config", {})
    config = welcome_config.setdefault(group_id, {"enabled": False, "message": "Bienvenue {username} !"})

    config["enabled"] = not config["enabled"]
    await save_data(context)

    await show_welcome_config(update, context)


async def toggle_antispam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Active ou désactive l'anti-spam pour le groupe sélectionné."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    group_id = context.user_data.get("selected_group_id")
    if group_id is None:
        await show_main(update, context)
        return

    group_id = str(group_id)
    persistent = context.bot_data.setdefault("persistent", {})
    user_pdata = persistent.setdefault(user_id, {})
    antispam_config = user_pdata.setdefault("antispam_config", {})
    config = antispam_config.setdefault(group_id, {
        "enabled": False,
        "block_links": True,
        "block_repeated": False
    })

    config["enabled"] = not config["enabled"]
    await save_data(context)

    await show_antispam_config(update, context)


async def toggle_block_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Active/désactive le blocage des liens."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    group_id = context.user_data.get("selected_group_id")
    if group_id is None:
        await show_main(update, context)
        return

    group_id = str(group_id)
    persistent = context.bot_data.setdefault("persistent", {})
    user_pdata = persistent.setdefault(user_id, {})
    antispam_config = user_pdata.setdefault("antispam_config", {})
    config = antispam_config.setdefault(group_id, {
        "enabled": False,
        "block_links": True,
        "block_repeated": False
    })
    config["block_links"] = not config.get("block_links", True)
    await save_data(context)
    await show_antispam_config(update, context)


async def toggle_block_repeated(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Active/désactive le blocage des messages répétitifs."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    group_id = context.user_data.get("selected_group_id")
    if group_id is None:
        await show_main(update, context)
        return

    group_id = str(group_id)
    persistent = context.bot_data.setdefault("persistent", {})
    user_pdata = persistent.setdefault(user_id, {})
    antispam_config = user_pdata.setdefault("antispam_config", {})
    config = antispam_config.setdefault(group_id, {
        "enabled": False,
        "block_links": True,
        "block_repeated": False
    })
    config["block_repeated"] = not config.get("block_repeated", False)
    await save_data(context)
    await show_antispam_config(update, context)
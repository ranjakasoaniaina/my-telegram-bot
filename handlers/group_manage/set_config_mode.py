# handlers/group_manage/set_config_mode.py

from telegram import Update
from telegram.ext import ContextTypes
from handlers.shared.group_eligibility import groups_entry

async def set_config_mode_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data.pop("group_filter_mode", None)
    context.user_data["config_mode"] = "welcome"
    await groups_entry(update, context)

async def set_config_mode_antispam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data.pop("group_filter_mode", None)
    context.user_data["config_mode"] = "antispam"
    await groups_entry(update, context)

async def refresh_group_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Nettoie le mode de filtrage et rafraîchit la liste des groupes."""
    query = update.callback_query
    await query.answer()
    context.user_data.pop("group_filter_mode", None)
    await groups_entry(update, context)
# utils.py

from telegram import Update
from telegram.ext import ContextTypes
from menu import SCREENS
from texts import t


# ---------- Navigation universelle ----------
async def retour(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère le bouton Retour universel (callback_data='nav:back')."""
    query = update.callback_query
    await query.answer()

    step_parent = context.user_data.get("step_parent")
    menu_parent = context.user_data.get("menu_parent")

    if step_parent is not None:
        target = step_parent
    elif menu_parent is not None:
        target = menu_parent
    else:
        target = "main"

    show_func = SCREENS.get(target, SCREENS["main"])
    await show_func(update, context)
# utils.py

from datetime import datetime
from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from config import OWNER_ID
from storage import save_data
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


# ---------- Décorateur propriétaire + compteur visiteur ----------
def owner_only(handler):
    @wraps(handler)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != OWNER_ID:
            # ----- Enregistrement de l'interaction active -----
            stats = context.bot_data.setdefault("persistent", {}).setdefault("vitrine_stats", {})
            today = datetime.now().strftime("%Y-%m-%d")
            daily = stats.setdefault("daily", {})
            day_data = daily.setdefault(today, {"unique_visitors": {}, "clicks_reserved": 0})
            user_id = str(update.effective_user.id)
            day_data["unique_visitors"][user_id] = True
            day_data.setdefault("clicking_visitors", {})[user_id] = True   # ← ligne ajoutée
            day_data["clicks_reserved"] = day_data.get("clicks_reserved", 0) + 1
            stats.setdefault("unique_visitors_global", {})[user_id] = True
            stats.setdefault("clicking_visitors_global", {})[user_id] = True   # ← ligne ajoutée
            stats["total_clicks_reserved"] = stats.get("total_clicks_reserved", 0) + 1
            await save_data(context)

            lang = context.user_data.get("lang", "fr")
            await update.callback_query.answer(
                t("error_owner_only", lang),
                show_alert=True
            )
            return
        return await handler(update, context)
    return wrapped
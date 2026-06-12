
import re
from telegram import Update
from telegram.ext import ContextTypes
from menu.groups.welcome import show_welcome_config
from menu.groups.antispam import show_antispam_config
from menu.show_main import show_main   # uniquement pour le fallback


async def select_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Capture 'group:select:<id>', stocke l'id et le titre, puis ouvre la bonne config."""
    query = update.callback_query
    await query.answer()

    data = query.data
    match = re.search(r"group:select:(.+)", data)
    if not match:
        return
    group_id_str = match.group(1)
    try:
        group_id = int(group_id_str)
    except ValueError:
        group_id = group_id_str

    titre = f"Groupe {group_id}"
    eligible = context.user_data.get("eligible_groups", [])
    for g in eligible:
        if g["id"] == group_id:
            titre = g["title"]
            break

    context.user_data["selected_group_id"] = group_id
    context.user_data["selected_group_title"] = titre

    # Redirection selon le mode choisi
    mode = context.user_data.get("config_mode")
    if mode == "welcome":
        await show_welcome_config(update, context)
    elif mode == "antispam":
        await show_antispam_config(update, context)
    else:
        # Fallback (ne devrait pas arriver)
        await show_main(update, context)
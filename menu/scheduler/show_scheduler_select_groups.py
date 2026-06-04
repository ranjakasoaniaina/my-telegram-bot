

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message



async def show_scheduler_select_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche la liste des groupes éligibles avec sélection multiple (toggle)."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")
    groupes = context.user_data.get("eligible_groups", [])
    selected_ids = context.user_data.get("scheduler_selected_group_ids", [])

    if groupes:
        texte = t("scheduler_create_group_select", lang)
    else:
        texte = t("error_no_eligible_groups", lang)

    boutons = []
    for groupe in groupes:
        gid = groupe["id"]
        titre = groupe["title"]
        prefixe = "☑" if gid in selected_ids else "☐"
        boutons.append([
            InlineKeyboardButton(
                f"{prefixe} {titre}",
                callback_data=f"scheduler:toggle_group:{gid}"
            )
        ])

    # Ligne de validation et retour
    ligne_actions = []
    if selected_ids:
        ligne_actions.append(
            InlineKeyboardButton(t("validate_selection", lang), callback_data="scheduler:groups_validated")
        )
    ligne_actions.append(
        InlineKeyboardButton(t("back", lang), callback_data="nav:back")
    )
    boutons.append(ligne_actions)

    clavier = InlineKeyboardMarkup(boutons)

    # Navigation
    context.user_data["current_screen"] = "scheduler_select_groups"
    context.user_data["step_parent"] = "scheduler_main"
    context.user_data["menu_parent"] = "main"

    # Affichage (édition ou envoi)
    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        await display_message(update, context, texte, clavier)
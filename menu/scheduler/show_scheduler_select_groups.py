# menu/scheduler/show_scheduler_select_groups.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message, estimate_width, pad_to_width
from config import MAX_GROUP_NAME_LENGTH


async def show_scheduler_select_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche la liste des groupes éligibles avec sélection multiple (toggle) pour un envoi programmé."""
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

    # --- Construction des labels avec troncature ---
    labels = []
    for groupe in groupes:
        titre = groupe["title"]
        if len(titre) > MAX_GROUP_NAME_LENGTH:
            titre = titre[:MAX_GROUP_NAME_LENGTH].rstrip() + "…"
        prefixe = "☑" if groupe["id"] in selected_ids else "☐"
        labels.append((f"{prefixe} {titre}", groupe["id"]))

    # --- Alignement ---
    widths = [estimate_width(l[0]) for l in labels]
    target = max(widths) if widths else 0
    padded_labels = [pad_to_width(l[0], target) for l in labels]

    # --- Création des boutons ---
    boutons = []
    for (_, gid), libelle in zip(labels, padded_labels):
        boutons.append([
            InlineKeyboardButton(
                libelle,
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

    # Affichage délégué
    await display_message(update, context, texte, clavier)
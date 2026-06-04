
# menu/groups/show_group_menu.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t


async def show_group_config_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Écran intermédiaire : choisir entre Bienvenue et Anti-spam."""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get("lang", "fr")
    texte = t("group_config_choice", lang)

    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("group_config_welcome", lang), callback_data="config_mode:welcome")],
        [InlineKeyboardButton(t("group_config_antispam", lang), callback_data="config_mode:antispam")],
        [InlineKeyboardButton(t("back", lang), callback_data="nav:back")]
    ])

    context.user_data["current_screen"] = "group_config_choice"
    context.user_data["step_parent"] = None
    context.user_data["menu_parent"] = "main"

    await query.edit_message_text(text=texte, reply_markup=clavier)


async def show_group_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche la liste des groupes éligibles sous forme de boutons."""

    lang = context.user_data.get("lang", "fr")
    # 1. Récupérer les données
    groupes = context.user_data.get("eligible_groups", [])
    # 2. Construire le texte
    if groupes:
        texte = t("group_list_title", lang)
    else:
        texte = t("group_list_empty", lang)
    # 3. Construire le clavier
    boutons = []
    for groupe in groupes:
        boutons.append([
            InlineKeyboardButton(
                groupe["title"],
                callback_data=f"group:select:{groupe['id']}"
            )
        ])
    boutons.append([
        InlineKeyboardButton(t("back", lang), callback_data="nav:back")
    ])
    # Bouton Rafraîchir
    boutons.append([
        InlineKeyboardButton(t("group_list_refresh", lang), callback_data="group:refresh")
    ])

    clavier = InlineKeyboardMarkup(boutons)
    # 4. Mettre à jour les champs de navigation
    context.user_data["current_screen"] = "group_list"
    context.user_data["step_parent"] = "group_config_choice"  # ← modifié pour pointer vers le choix
    context.user_data["menu_parent"] = "main"

    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=texte, reply_markup=clavier)
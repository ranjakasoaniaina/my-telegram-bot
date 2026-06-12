# menu/groups/show_group_menu.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t
from menu.display_utils import display_message, estimate_width, pad_to_width
from config import MAX_GROUP_NAME_LENGTH


async def show_group_config_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Écran intermédiaire : choisir entre Bienvenue et Anti-spam."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")
    texte = t("group_config_choice", lang)

    # --- Boutons alignés (💬 Bienvenue / 🛡 Anti-spam) ---
    labels = [
        t("group_config_welcome", lang),
        t("group_config_antispam", lang),
    ]
    widths = [estimate_width(l) for l in labels]
    target = max(widths) if widths else 0
    padded = [pad_to_width(l, target) for l in labels]

    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(padded[0], callback_data="config_mode:welcome")],
        [InlineKeyboardButton(padded[1], callback_data="config_mode:antispam")],
        [InlineKeyboardButton(t("back", lang), callback_data="nav:back")]
    ])

    context.user_data["current_screen"] = "group_config_choice"
    context.user_data["step_parent"] = None
    context.user_data["menu_parent"] = "main"

    await display_message(update, context, texte, clavier)


async def show_group_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche la liste des groupes éligibles avec noms tronqués et alignés."""

    lang = context.user_data.get("lang", "fr")

    # 1. Récupérer les données
    groupes = context.user_data.get("eligible_groups", [])

    # 2. Construire le texte
    if groupes:
        texte = t("group_list_title", lang)
    else:
        texte = t("group_list_empty", lang)

    # 3. Construire les boutons avec alignement
    boutons = []
    if groupes:
        # Troncature et alignement des noms de groupes
        labels = []
        for groupe in groupes:
            titre = groupe["title"]
            if len(titre) > MAX_GROUP_NAME_LENGTH:
                titre = titre[:MAX_GROUP_NAME_LENGTH].rstrip() + "…"
            labels.append((titre, groupe["id"]))

        widths = [estimate_width(l[0]) for l in labels]
        target = max(widths) if widths else 0
        padded_labels = [pad_to_width(l[0], target) for l in labels]

        for (_, gid), libelle in zip(labels, padded_labels):
            boutons.append([
                InlineKeyboardButton(libelle, callback_data=f"group:select:{gid}")
            ])

    # 4. Boutons Rafraîchir puis Retour
    boutons.append([
        InlineKeyboardButton(t("group_list_refresh", lang), callback_data="group:refresh")
    ])
    boutons.append([
        InlineKeyboardButton(t("back", lang), callback_data="nav:back")
    ])

    clavier = InlineKeyboardMarkup(boutons)

    # 5. Navigation
    context.user_data["current_screen"] = "group_list"
    context.user_data["step_parent"] = "group_config_choice"
    context.user_data["menu_parent"] = "main"

    await display_message(update, context, texte, clavier)
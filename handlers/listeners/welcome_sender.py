# handlers/listeners/welcome_sender.py

from telegram import Update
from telegram.ext import ContextTypes
from texts import t


async def send_welcome_to_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envoie le message de bienvenue personnalisé aux nouveaux membres, si activé."""
    chat = update.effective_chat

    if chat.type not in ("group", "supergroup"):
        return

    new_members = update.message.new_chat_members
    if not new_members:
        return

    chat_id = str(chat.id)
    persistent = context.bot_data.get("persistent", {})

    # Chercher la configuration de bienvenue active pour ce groupe
    for user_data in persistent.values():
        welcome_config = user_data.get("welcome_config", {})
        group_config = welcome_config.get(chat_id)
        if group_config and group_config.get("enabled", False):
            # Utilise le message configuré, sinon le message par défaut localisé
            default_msg = t("welcome_default", "fr")  # langue du propriétaire par défaut
            message_template = group_config.get("message", default_msg)
            break
    else:
        return  # Aucune config active → rien à envoyer

    # Envoyer le message à chaque nouveau membre
    for member in new_members:
        username = f"@{member.username}" if member.username else member.full_name
        text = message_template.format(
            username=username,
            group_name=chat.title or "ce groupe"
        )

        try:
            await context.bot.send_message(chat_id=chat.id, text=text)
        except Exception:
            pass  # Permission manquante, bot supprimé, etc.
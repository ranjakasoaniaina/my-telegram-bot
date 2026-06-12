# handlers/listeners/spam_checker.py

import re
from telegram import Update
from telegram.ext import ContextTypes

# Stockage temporaire des derniers messages par groupe/utilisateur
_recent_messages = {}  # {chat_id: {user_id: [texte1, texte2, ...]}}


def _has_url(text: str) -> bool:
    """Détecte si le texte contient une URL."""
    pattern = r'https?://\S+|www\.\S+|t\.me/\S+'
    return bool(re.search(pattern, text))


async def check_spam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Analyse un message et supprime si spam détecté (selon la config du groupe)."""
    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        return

    message = update.message
    if not message or not message.text:
        return

    user = update.effective_user
    if user is None:
        return

    chat_id = str(chat.id)
    user_id = user.id

    # Ne pas filtrer les administrateurs
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status in ("administrator", "creator"):
            return
    except Exception:
        return

    # Récupérer la configuration anti‑spam pour ce groupe
    persistent = context.bot_data.get("persistent", {})
    config = None
    for user_data in persistent.values():
        antispam_config = user_data.get("antispam_config", {})
        if chat_id in antispam_config:
            config = antispam_config[chat_id]
            break

    if not config or not config.get("enabled", False):
        return  # Anti‑spam non activé

    block_links = config.get("block_links", True)
    block_repeated = config.get("block_repeated", False)
    text = message.text or ""

    spam = False

    # Règle 1 : lien
    if block_links and _has_url(text):
        spam = True

    # Règle 2 : répétition
    if block_repeated:
        chat_recent = _recent_messages.setdefault(chat_id, {})
        user_recent = chat_recent.setdefault(user_id, [])
        if text in user_recent:
            spam = True
        else:
            user_recent.append(text)
            if len(user_recent) > 5:  # garder les 5 derniers messages
                user_recent.pop(0)

    if spam:
        try:
            await context.bot.delete_message(chat_id=chat.id, message_id=message.message_id)
        except Exception:
            pass  # permission manquante, message déjà supprimé, etc.
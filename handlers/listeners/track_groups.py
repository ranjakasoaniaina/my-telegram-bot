from telegram import Update
from telegram.ext import ContextTypes


async def track_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enregistre silencieusement les groupes lorsque le bot est ajouté ou que ses droits changent."""
    chat = update.my_chat_member.chat

    if chat.type not in ("group", "supergroup"):
        return

    new_status = update.my_chat_member.new_chat_member.status
    known = context.bot_data.setdefault("known_groups", {})

    if new_status in ("administrator", "member"):
        known[chat.id] = {"title": chat.title or f"Groupe {chat.id}"}
    elif new_status == "left":
        known.pop(chat.id, None)


async def track_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enregistre silencieusement tout groupe où un message est posté (filet de sécurité)."""
    chat = update.effective_chat

    if chat.type not in ("group", "supergroup"):
        return

    known = context.bot_data.setdefault("known_groups", {})
    known[chat.id] = {"title": chat.title or f"Groupe {chat.id}"}
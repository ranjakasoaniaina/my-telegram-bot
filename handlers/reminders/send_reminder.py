# handlers/reminders/send_reminder.py

from telegram.ext import CallbackContext


async def send_reminder(context: CallbackContext) -> None:
    """Envoie le rappel selon le mode (privé ou groupes)."""
    job_data = context.job.data
    user_id = job_data["user_id"]
    mode = job_data["mode"]
    text = job_data["text"]
    group_ids = job_data.get("group_ids", [])

    if mode == "private":
        try:
            await context.bot.send_message(chat_id=int(user_id), text=f"⏰ Rappel : {text}")
        except Exception:
            pass
    elif mode == "groups":
        for gid in group_ids:
            try:
                await context.bot.send_message(chat_id=gid, text=f"⏰ Rappel : {text}")
            except Exception:
                pass
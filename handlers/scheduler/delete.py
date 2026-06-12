# handlers/scheduler/delete.py

from telegram import Update
from telegram.ext import ContextTypes
from menu.scheduler.show_scheduler_delete_list import show_scheduler_delete_list
import re
from storage import save_data
from menu.scheduler.show_scheduler_main import show_scheduler_main
from texts import t


async def enter_delete_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Point d'entrée de la suppression des messages programmés."""
    query = update.callback_query
    await query.answer()
    context.user_data["scheduler_action"] = "delete"
    context.user_data["scheduler_delete_ids"] = []
    await show_scheduler_delete_list(update, context)


async def toggle_delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ajoute ou retire un message de la sélection de suppression."""
    query = update.callback_query
    await query.answer()

    data = query.data
    match = re.search(r"scheduler:delete_toggle:(.+)", data)
    if not match:
        return
    msg_id = match.group(1)

    delete_ids = context.user_data.setdefault("scheduler_delete_ids", [])
    if msg_id in delete_ids:
        delete_ids.remove(msg_id)
    else:
        delete_ids.append(msg_id)

    await show_scheduler_delete_list(update, context)


async def select_all_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sélectionne tous les messages pour suppression."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    persistent = context.bot_data.get("persistent", {})
    messages = persistent.get(user_id, {}).get("scheduled_messages", [])
    context.user_data["scheduler_delete_ids"] = [m["id"] for m in messages]
    await show_scheduler_delete_list(update, context)


async def deselect_all_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Désélectionne tous les messages."""
    query = update.callback_query
    await query.answer()
    context.user_data["scheduler_delete_ids"] = []
    await show_scheduler_delete_list(update, context)


async def confirm_delete_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Supprime effectivement les messages sélectionnés (jobs + données persistantes)."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    lang = context.user_data.get("lang", "fr")
    delete_ids = context.user_data.get("scheduler_delete_ids", [])

    if not delete_ids:
        await query.answer(t("error_no_selection_message", lang), show_alert=True)
        return

    persistent = context.bot_data.setdefault("persistent", {})
    messages = persistent.get(user_id, {}).get("scheduled_messages", [])

    for msg_id in delete_ids:
        # Annuler le job correspondant
        for job in context.application.job_queue.jobs():
            if job.name == msg_id:   # car job_id == msg_id
                job.schedule_removal()
                break

    # Supprimer les entrées persistantes
    persistent[user_id]["scheduled_messages"] = [m for m in messages if m["id"] not in delete_ids]
    await save_data(context)

    # Nettoyage
    context.user_data.pop("scheduler_delete_ids", None)
    context.user_data.pop("scheduler_action", None)

    context.user_data["action_success_msg_key"] = "success_scheduler_deleted"
    await show_scheduler_main(update, context)
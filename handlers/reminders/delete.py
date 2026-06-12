# handlers/reminders/delete.py

from telegram import Update
from telegram.ext import ContextTypes
from menu.reminders.show_reminder_delete_list import show_reminder_delete_list
import re
from storage import save_data
from menu.reminders.show_reminder_main import show_reminder_main
from texts import t


async def enter_delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Point d'entrée de la suppression des rappels."""
    query = update.callback_query
    await query.answer()
    context.user_data["reminder_action"] = "delete"
    context.user_data["reminder_delete_ids"] = []
    await show_reminder_delete_list(update, context)


async def toggle_delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ajoute ou retire un rappel de la sélection de suppression."""
    query = update.callback_query
    await query.answer()

    data = query.data
    match = re.search(r"reminder:delete_toggle:(.+)", data)
    if not match:
        return
    rem_id = match.group(1)

    delete_ids = context.user_data.setdefault("reminder_delete_ids", [])
    if rem_id in delete_ids:
        delete_ids.remove(rem_id)
    else:
        delete_ids.append(rem_id)

    await show_reminder_delete_list(update, context)


async def select_all_delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sélectionne tous les rappels pour suppression."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    persistent = context.bot_data.get("persistent", {})
    reminders = persistent.get(user_id, {}).get("reminders", [])
    context.user_data["reminder_delete_ids"] = [r["id"] for r in reminders]
    await show_reminder_delete_list(update, context)


async def deselect_all_delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Désélectionne tous les rappels."""
    query = update.callback_query
    await query.answer()
    context.user_data["reminder_delete_ids"] = []
    await show_reminder_delete_list(update, context)


async def confirm_delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Supprime effectivement les rappels sélectionnés (jobs + données persistantes)."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    lang = context.user_data.get("lang", "fr")
    delete_ids = context.user_data.get("reminder_delete_ids", [])

    if not delete_ids:
        await query.answer(t("error_no_reminder_selected", lang), show_alert=True)
        return

    persistent = context.bot_data.setdefault("persistent", {})
    reminders = persistent.get(user_id, {}).get("reminders", [])

    for rem_id in delete_ids:
        # Annuler le job correspondant
        for job in context.application.job_queue.jobs():
            if job.name == rem_id:
                job.schedule_removal()
                break

    # Supprimer les entrées persistantes
    persistent[user_id]["reminders"] = [r for r in reminders if r["id"] not in delete_ids]
    await save_data(context)

    # Nettoyage
    context.user_data.pop("reminder_delete_ids", None)
    context.user_data.pop("reminder_action", None)

    context.user_data["action_success_msg_key"] = "success_reminder_deleted"
    await show_reminder_main(update, context)
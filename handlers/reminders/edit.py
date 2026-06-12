# handlers/reminders/edit.py

from telegram import Update
from telegram.ext import ContextTypes
from menu.reminders.show_reminder_edit_list import show_reminder_edit_list
import re
from menu.reminders.show_reminder_enter_datetime import show_reminder_enter_datetime
from menu.reminders.show_reminder_enter_recurrence import show_reminder_enter_recurrence
from menu.reminders.show_reminder_enter_text import show_reminder_enter_text
from menu.reminders.show_reminder_confirm import show_reminder_confirm
import uuid
from datetime import datetime, timezone, timedelta
from storage import save_data
from handlers.reminders.send_reminder import send_reminder
from menu.reminders.show_reminder_main import show_reminder_main
from texts import t
from config import TIMEZONE_OFFSET


async def enter_edit_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Point d'entrée de la modification d'un rappel."""
    query = update.callback_query
    await query.answer()
    context.user_data["reminder_action"] = "edit"
    await show_reminder_edit_list(update, context)


async def select_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Charge le rappel sélectionné dans le draft et lance la modification."""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get("lang", "fr")
    data = query.data
    match = re.search(r"reminder:select:(.+)", data)
    if not match:
        return
    rem_id = match.group(1)

    user_id = str(update.effective_user.id)
    persistent = context.bot_data.get("persistent", {})
    reminders = persistent.get(user_id, {}).get("reminders", [])

    rem = next((r for r in reminders if r["id"] == rem_id), None)
    if rem is None:
        await query.answer(t("error_reminder_not_found", lang), show_alert=True)
        return

    # Stocker l'id en cours d'édition et pré-remplir le draft
    context.user_data["reminder_edit_id"] = rem_id
    context.user_data["reminder_mode"] = rem["mode"]
    context.user_data["reminder_selected_group_ids"] = rem.get("group_ids", [])
    context.user_data["reminder_draft"] = {
        "datetime": rem["datetime"],
        "recurrence": rem["recurrence"],
        "text": rem["text"]
    }

    # Démarrer par la première étape modifiable (date/heure)
    await show_reminder_enter_datetime(update, context)


async def skip_reminder_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get("lang", "fr")
    draft = context.user_data.get("reminder_draft", {})
    dt_str = draft.get("datetime", "")

    # Vérifier que la date n'est pas déjà passée
    if dt_str:
        from datetime import datetime
        dt = datetime.fromisoformat(dt_str)
        # Comparer en ignorant le fuseau pour simplifier (l'heure locale est déjà saisie)
        if dt <= datetime.now():
            await query.answer(t("error_date_past", lang), show_alert=True)
            return

    await show_reminder_enter_recurrence(update, context)



async def skip_reminder_recurrence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await show_reminder_enter_text(update, context)


async def skip_reminder_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await show_reminder_confirm(update, context)


async def confirm_reminder_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    lang = context.user_data.get("lang", "fr")
    rem_id = context.user_data.get("reminder_edit_id")
    mode = context.user_data.get("reminder_mode", "private")
    draft = context.user_data.get("reminder_draft", {})
    selected_ids = context.user_data.get("reminder_selected_group_ids", [])

    if not rem_id or not draft:
        await query.answer(t("error_incomplete_data", lang), show_alert=True)
        await show_reminder_main(update, context)
        return

    persistent = context.bot_data.setdefault("persistent", {})
    user_pdata = persistent.setdefault(user_id, {})
    reminders = user_pdata.setdefault("reminders", [])

    rem = next((r for r in reminders if r["id"] == rem_id), None)
    if rem is None:
        await query.answer(t("error_reminder_not_found", lang), show_alert=True)
        await show_reminder_main(update, context)
        return

    # Mettre à jour les champs
    rem["datetime"] = draft["datetime"]
    rem["recurrence"] = draft["recurrence"]
    rem["text"] = draft["text"]
    rem["group_ids"] = selected_ids if mode == "groups" else []
    rem["mode"] = mode

    # Annuler l'ancien job
    old_job_id = rem.get("job_id")
    if old_job_id:
        for job in context.application.job_queue.jobs():
            if job.name == old_job_id:
                job.schedule_removal()

    # Recréer le job avec les nouveaux paramètres
    dt_str = draft["datetime"]
    recurrence = draft["recurrence"]
    dt = datetime.fromisoformat(dt_str)

    # --- Conversion de l'heure locale en UTC ---
    match = re.match(r"([+-])(\d{2}):(\d{2})", TIMEZONE_OFFSET)
    if match:
        sign = 1 if match.group(1) == "+" else -1
        hours = int(match.group(2))
        minutes = int(match.group(3))
        offset = timedelta(hours=hours, minutes=minutes) * sign
        tz = timezone(offset)
        dt = dt.replace(tzinfo=tz)          # heure locale saisie
        dt_utc = dt.astimezone(timezone.utc) # conversion en UTC
    else:
        dt_utc = dt

    new_job_id = f"rem_{uuid.uuid4().hex[:8]}"

    if recurrence == "daily":
        context.application.job_queue.run_daily(
            send_reminder,
            time=dt_utc.time(),
            name=new_job_id,
            data={"user_id": user_id, "mode": mode, "group_ids": selected_ids, "text": draft["text"]}
        )
    elif recurrence == "weekly":
        context.application.job_queue.run_daily(
            send_reminder,
            time=dt_utc.time(),
            days=(dt_utc.weekday(),),
            name=new_job_id,
            data={"user_id": user_id, "mode": mode, "group_ids": selected_ids, "text": draft["text"]}
        )
    elif recurrence == "monthly":
        interval_seconds = 30 * 24 * 3600
        context.application.job_queue.run_repeating(
            send_reminder,
            interval=interval_seconds,
            first=dt_utc,
            name=new_job_id,
            data={"user_id": user_id, "mode": mode, "group_ids": selected_ids, "text": draft["text"]}
        )
    elif recurrence == "once":
        context.application.job_queue.run_once(
            send_reminder,
            when=dt_utc,
            name=new_job_id,
            data={"user_id": user_id, "mode": mode, "group_ids": selected_ids, "text": draft["text"]}
        )

    rem["job_id"] = new_job_id
    await save_data(context)

    # Nettoyage
    context.user_data.pop("reminder_draft", None)
    context.user_data.pop("reminder_selected_group_ids", None)
    context.user_data.pop("reminder_mode", None)
    context.user_data.pop("reminder_edit_id", None)
    context.user_data.pop("group_filter_mode", None)

    context.user_data["action_success_msg_key"] = "success_reminder_edited"
    await show_reminder_main(update, context)
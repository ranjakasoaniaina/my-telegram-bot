# handlers/reminders/create.py

from telegram import Update
from telegram.ext import ContextTypes
from handlers.shared.group_eligibility import groups_entry
from menu.reminders.show_reminder_enter_datetime import show_reminder_enter_datetime
import re
from menu.reminders.show_reminder_select_groups import show_reminder_select_groups
from menu.reminders.show_reminder_enter_text import show_reminder_enter_text
import uuid
from datetime import datetime, timezone, timedelta
from storage import save_data
from menu.reminders.show_reminder_main import show_reminder_main
from handlers.reminders.send_reminder import send_reminder
from texts import t
from config import TIMEZONE_OFFSET


async def set_reminder_mode_private(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Configure le rappel en mode privé et passe à la saisie de la date/heure."""
    query = update.callback_query
    await query.answer()

    context.user_data["reminder_mode"] = "private"
    context.user_data["reminder_draft"] = {}
    context.user_data["reminder_selected_group_ids"] = []
    await show_reminder_enter_datetime(update, context)


async def set_reminder_mode_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Configure le rappel en mode groupes et lance la sélection des groupes éligibles."""
    query = update.callback_query
    await query.answer()

    context.user_data["reminder_mode"] = "groups"
    context.user_data["reminder_draft"] = {}
    context.user_data["reminder_selected_group_ids"] = []
    context.user_data["group_filter_mode"] = "reminder"
    await groups_entry(update, context)


async def toggle_reminder_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ajoute ou retire un groupe de la sélection temporaire pour un rappel."""
    query = update.callback_query
    await query.answer()
    data = query.data
    match = re.search(r"reminder:toggle_group:(.+)", data)
    if not match:
        return
    try:
        group_id = int(match.group(1))
    except ValueError:
        group_id = match.group(1)
    selected = context.user_data.setdefault("reminder_selected_group_ids", [])
    if group_id in selected:
        selected.remove(group_id)
    else:
        selected.append(group_id)
    await show_reminder_select_groups(update, context)


async def validate_reminder_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Vérifie qu'au moins un groupe est sélectionné, puis passe à la saisie de la date/heure."""
    query = update.callback_query
    await query.answer()
    selected = context.user_data.get("reminder_selected_group_ids", [])
    if not selected:
        lang = context.user_data.get("lang", "fr")
        await query.answer(t("error_no_selection", lang), show_alert=True)
        return
    await show_reminder_enter_datetime(update, context)


async def set_reminder_recurrence_daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    draft = context.user_data.setdefault("reminder_draft", {})
    draft["recurrence"] = "daily"
    await show_reminder_enter_text(update, context)


async def set_reminder_recurrence_weekly(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    draft = context.user_data.setdefault("reminder_draft", {})
    draft["recurrence"] = "weekly"
    await show_reminder_enter_text(update, context)


async def set_reminder_recurrence_monthly(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    draft = context.user_data.setdefault("reminder_draft", {})
    draft["recurrence"] = "monthly"
    await show_reminder_enter_text(update, context)


async def set_reminder_recurrence_once(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Définit la récurrence sur 'une seule fois'."""
    query = update.callback_query
    await query.answer()
    draft = context.user_data.setdefault("reminder_draft", {})
    draft["recurrence"] = "once"
    await show_reminder_enter_text(update, context)


async def confirm_reminder_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enregistre le rappel et planifie le job."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    lang = context.user_data.get("lang", "fr")
    mode = context.user_data.get("reminder_mode", "private")
    draft = context.user_data.get("reminder_draft", {})
    selected_ids = context.user_data.get("reminder_selected_group_ids", [])

    if not draft or (mode == "groups" and not selected_ids):
        await query.answer(t("error_incomplete_data", lang), show_alert=True)
        await show_reminder_main(update, context)
        return

    text_msg = draft["text"]
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
        dt = dt.replace(tzinfo=tz)          # fuseau local
        dt_utc = dt.astimezone(timezone.utc) # conversion en UTC
    else:
        dt_utc = dt

    rem_id = f"rem_{uuid.uuid4().hex[:8]}"

    # Planification selon la récurrence
    if recurrence == "daily":
        context.application.job_queue.run_daily(
            send_reminder,
            time=dt_utc.time(),
            name=rem_id,
            data={"user_id": user_id, "mode": mode, "group_ids": selected_ids, "text": text_msg}
        )
    elif recurrence == "weekly":
        context.application.job_queue.run_daily(
            send_reminder,
            time=dt_utc.time(),
            days=(dt_utc.weekday(),),
            name=rem_id,
            data={"user_id": user_id, "mode": mode, "group_ids": selected_ids, "text": text_msg}
        )
    elif recurrence == "monthly":
        interval_seconds = 30 * 24 * 3600
        context.application.job_queue.run_repeating(
            send_reminder,
            interval=interval_seconds,
            first=dt_utc,
            name=rem_id,
            data={"user_id": user_id, "mode": mode, "group_ids": selected_ids, "text": text_msg}
        )
    elif recurrence == "once":
        context.application.job_queue.run_once(
            send_reminder,
            when=dt_utc,
            name=rem_id,
            data={"user_id": user_id, "mode": mode, "group_ids": selected_ids, "text": text_msg}
        )
    else:
        await query.answer(t("error_unknown_recurrence", lang), show_alert=True)
        return

    # Enregistrement persistant
    persistent = context.bot_data.setdefault("persistent", {})
    user_pdata = persistent.setdefault(user_id, {})
    reminders = user_pdata.setdefault("reminders", [])
    reminders.append({
        "id": rem_id,
        "mode": mode,
        "group_ids": selected_ids if mode == "groups" else [],
        "datetime": dt_str,         # heure locale
        "recurrence": recurrence,
        "text": text_msg,
        "job_id": rem_id
    })
    await save_data(context)

    # Nettoyage et redirection
    context.user_data.pop("reminder_draft", None)
    context.user_data.pop("reminder_selected_group_ids", None)
    context.user_data.pop("reminder_mode", None)
    context.user_data.pop("group_filter_mode", None)

    context.user_data["action_success_msg_key"] = "success_reminder_created"
    await show_reminder_main(update, context)
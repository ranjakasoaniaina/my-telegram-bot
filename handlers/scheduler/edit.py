# handlers/scheduler/edit.py

import re
import uuid
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from storage import save_data
from config import MAX_SCHEDULER_DURATION_MINUTES
from texts import t

from menu.scheduler.show_scheduler_edit_list import show_scheduler_edit_list
from menu.scheduler.show_scheduler_enter_text import show_scheduler_enter_text
from menu.scheduler.show_scheduler_enter_interval import show_scheduler_enter_interval
from menu.scheduler.show_scheduler_enter_count import show_scheduler_enter_count
from menu.scheduler.show_scheduler_confirm import show_scheduler_confirm
from menu.scheduler.show_scheduler_main import show_scheduler_main


async def enter_edit_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Point d'entrée de la modification d'un message programmé."""
    query = update.callback_query
    await query.answer()
    context.user_data["scheduler_action"] = "edit"
    await show_scheduler_edit_list(update, context)


async def select_scheduler_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sélectionne un message programmé et pré-remplit le draft pour modification."""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get("lang", "fr")
    data = query.data
    match = re.search(r"scheduler:select:(.+)", data)
    if not match:
        return
    msg_id = match.group(1)

    user_id = str(update.effective_user.id)
    persistent = context.bot_data.get("persistent", {})
    messages = persistent.get(user_id, {}).get("scheduled_messages", [])

    msg = next((m for m in messages if m["id"] == msg_id), None)
    if msg is None:
        await query.answer(t("error_message_not_found", lang), show_alert=True)
        return

    context.user_data["scheduler_edit_msg_id"] = msg_id
    context.user_data["scheduler_draft"] = {
        "text": msg["text"],
        "interval": msg["interval_minutes"],
        "count": msg["max_sends"],
    }
    await show_scheduler_enter_text(update, context)


async def skip_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await show_scheduler_enter_interval(update, context)


async def skip_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await show_scheduler_enter_count(update, context)


async def skip_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await show_scheduler_confirm(update, context)


async def confirm_edit_scheduler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enregistre les modifications d'un message programmé et reprogramme le job."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    lang = context.user_data.get("lang", "fr")
    msg_id = context.user_data.get("scheduler_edit_msg_id")
    draft = context.user_data.get("scheduler_draft", {})

    if not msg_id or not draft:
        await query.answer(t("error_incomplete_data", lang), show_alert=True)
        await show_scheduler_main(update, context)
        return

    persistent = context.bot_data.setdefault("persistent", {})
    user_pdata = persistent.setdefault(user_id, {})
    messages = user_pdata.setdefault("scheduled_messages", [])

    entry = next((m for m in messages if m["id"] == msg_id), None)
    if entry is None:
        await query.answer(t("error_message_not_found", lang), show_alert=True)
        await show_scheduler_main(update, context)
        return

    # Mise à jour des champs modifiables
    entry["text"] = draft["text"]
    entry["interval_minutes"] = draft["interval"]
    entry["max_sends"] = draft["count"]
    # Réinitialiser le compteur d'envois
    entry["sent_count"] = 0

    # --- Recréer le job avec les nouveaux paramètres ---
    # 1. Annuler l'ancien job s'il existe encore
    old_job_id = entry.get("job_id")
    if old_job_id:
        for job in context.application.job_queue.jobs():
            if job.name == old_job_id:
                job.schedule_removal()

    # 2. Créer un nouvel identifiant de job
    new_job_id = f"scheduler_{uuid.uuid4().hex[:8]}"
    start_time = datetime.utcnow()
    text_msg = entry["text"]
    interval_min = entry["interval_minutes"]
    max_sends = entry["max_sends"]
    group_ids = entry["group_ids"]

    async def repeating_job(ctx):
        # Arrêt automatique après 24h
        if (datetime.utcnow() - start_time).total_seconds() / 60 > MAX_SCHEDULER_DURATION_MINUTES:
            for job in ctx.application.job_queue.jobs():
                if job.name == new_job_id:
                    job.schedule_removal()
            # Supprimer l'entrée persistante
            pers = ctx.bot_data.setdefault("persistent", {})
            msgs = pers.get(user_id, {}).get("scheduled_messages", [])
            pers[user_id]["scheduled_messages"] = [m for m in msgs if m["id"] != msg_id]
            await save_data(ctx)
            return

        pers = ctx.bot_data.setdefault("persistent", {})
        msgs = pers.get(user_id, {}).get("scheduled_messages", [])
        entry2 = next((m for m in msgs if m["id"] == msg_id), None)
        if entry2:
            entry2["sent_count"] = entry2.get("sent_count", 0) + 1
            if entry2["sent_count"] >= max_sends:
                for job in ctx.application.job_queue.jobs():
                    if job.name == new_job_id:
                        job.schedule_removal()
                # Supprimer l'entrée persistante
                pers[user_id]["scheduled_messages"] = [m for m in msgs if m["id"] != msg_id]
                await save_data(ctx)
                return
            # Envoi dans chaque groupe
            for gid in group_ids:
                try:
                    await ctx.bot.send_message(chat_id=gid, text=text_msg)
                except Exception:
                    pass

    context.application.job_queue.run_repeating(
        repeating_job,
        interval=interval_min * 60,
        first=interval_min * 60,
        name=new_job_id,
    )

    entry["job_id"] = new_job_id
    await save_data(context)

    # Nettoyage et redirection
    context.user_data.pop("scheduler_draft", None)
    context.user_data.pop("scheduler_edit_msg_id", None)
    context.user_data.pop("scheduler_selected_group_ids", None)
    context.user_data.pop("group_filter_mode", None)

    context.user_data["action_success_msg_key"] = "success_scheduler_edited"
    await show_scheduler_main(update, context)
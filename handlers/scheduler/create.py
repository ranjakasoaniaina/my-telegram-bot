# handlers/scheduler/create.py

import re
from telegram import Update
from telegram.ext import ContextTypes
from handlers.shared.group_eligibility import groups_entry
from menu.scheduler.show_scheduler_select_groups import show_scheduler_select_groups
from menu.scheduler.show_scheduler_enter_text import show_scheduler_enter_text
import uuid
from datetime import datetime
from storage import save_data
from config import MAX_SCHEDULER_DURATION_MINUTES
from menu.scheduler.show_scheduler_main import show_scheduler_main
from texts import t


async def enter_new_scheduler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Point d'entrée de la création d'un nouveau message programmé."""
    query = update.callback_query
    await query.answer()

    # 1. Mode de filtrage pour le scheduler (membre + can_send_messages)
    context.user_data["group_filter_mode"] = "scheduler"

    # 2. Réinitialiser les données temporaires de la création
    context.user_data["scheduler_selected_group_ids"] = []
    context.user_data["scheduler_draft"] = {}

    # 3. Lancer la vérification et l'affichage de la liste des groupes
    await groups_entry(update, context)


async def toggle_scheduler_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ajoute ou retire un groupe de la sélection temporaire."""
    query = update.callback_query
    await query.answer()

    # Extraire l'id du groupe depuis le callback_data
    data = query.data
    match = re.search(r"scheduler:toggle_group:(.+)", data)
    if not match:
        return
    try:
        group_id = int(match.group(1))
    except ValueError:
        group_id = match.group(1)

    selected = context.user_data.setdefault("scheduler_selected_group_ids", [])

    if group_id in selected:
        selected.remove(group_id)
    else:
        selected.append(group_id)

    # Rafraîchir l'affichage
    await show_scheduler_select_groups(update, context)


async def validate_scheduler_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Vérifie qu'au moins un groupe est sélectionné, puis passe à la saisie du texte."""
    query = update.callback_query
    await query.answer()

    selected = context.user_data.get("scheduler_selected_group_ids", [])
    if not selected:
        lang = context.user_data.get("lang", "fr")
        await query.answer(t("error_no_selection", lang), show_alert=True)
        return

    # La sélection est valide → passer à l'étape suivante (saisie du texte)
    await show_scheduler_enter_text(update, context)


async def confirm_create_scheduler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enregistre la programmation, envoie le premier message et planifie les répétitions."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    lang = context.user_data.get("lang", "fr")
    draft = context.user_data.get("scheduler_draft", {})
    selected_ids = context.user_data.get("scheduler_selected_group_ids", [])

    if not selected_ids or not draft:
        await query.answer(t("error_incomplete_data", lang), show_alert=True)
        await show_scheduler_main(update, context)
        return

    text_msg = draft["text"]
    interval_min = draft["interval"]
    max_sends = draft["count"]

    # --- 1. Envoi immédiat du premier message ---
    for gid in selected_ids:
        try:
            await context.bot.send_message(chat_id=gid, text=text_msg)
        except Exception:
            pass  # à logger plus tard si besoin

    # --- 2. Planification des répétitions ---
    job_id = f"scheduler_{uuid.uuid4().hex[:8]}"
    start_time = datetime.utcnow()

    async def repeating_job(ctx):
        # Arrêt automatique après 24h
        if (datetime.utcnow() - start_time).total_seconds() / 60 > MAX_SCHEDULER_DURATION_MINUTES:
            for job in ctx.application.job_queue.jobs():
                if job.name == job_id:
                    job.schedule_removal()
            # Supprimer l'entrée persistante
            persistent = ctx.bot_data.setdefault("persistent", {})
            msgs = persistent.get(user_id, {}).get("scheduled_messages", [])
            persistent[user_id]["scheduled_messages"] = [m for m in msgs if m["id"] != job_id]
            await save_data(ctx)
            return

        # Vérification du nombre d'envois
        persistent = ctx.bot_data.setdefault("persistent", {})
        msgs = persistent.get(user_id, {}).get("scheduled_messages", [])
        entry = next((m for m in msgs if m["id"] == job_id), None)
        if entry:
            entry["sent_count"] = entry.get("sent_count", 0) + 1
            if entry["sent_count"] >= max_sends:
                for job in ctx.application.job_queue.jobs():
                    if job.name == job_id:
                        job.schedule_removal()
                persistent[user_id]["scheduled_messages"] = [m for m in msgs if m["id"] != job_id]
                await save_data(ctx)
                return
            # Envoyer dans chaque groupe
            for gid in selected_ids:
                try:
                    await ctx.bot.send_message(chat_id=gid, text=text_msg)
                except Exception:
                    pass

    context.application.job_queue.run_repeating(
        repeating_job,
        interval=interval_min * 60,
        first=interval_min * 60,
        name=job_id
    )

    # --- 3. Enregistrement persistant ---
    persistent = context.bot_data.setdefault("persistent", {})
    user_pdata = persistent.setdefault(user_id, {})
    messages = user_pdata.setdefault("scheduled_messages", [])
    messages.append({
        "id": job_id,
        "group_ids": selected_ids,
        "text": text_msg,
        "interval_minutes": interval_min,
        "max_sends": max_sends,
        "sent_count": 1,
        "created_at": start_time.isoformat(),
        "job_id": job_id
    })
    await save_data(context)

    # --- 4. Nettoyage et redirection ---
    context.user_data.pop("scheduler_draft", None)
    context.user_data.pop("scheduler_selected_group_ids", None)
    context.user_data.pop("group_filter_mode", None)

    # Stocker la clé de succès pour que l'écran suivant puisse la traduire
    context.user_data["action_success_msg_key"] = "success_scheduler_created"
    await show_scheduler_main(update, context)
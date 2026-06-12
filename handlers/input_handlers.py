# handlers/input_handlers.py

from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from storage import save_data
from config import MIN_SCHEDULER_INTERVAL
from texts import t

from menu.groups.welcome import show_welcome_config
from menu.scheduler.show_scheduler_enter_interval import show_scheduler_enter_interval
from menu.scheduler.show_scheduler_enter_count import show_scheduler_enter_count
from menu.scheduler.show_scheduler_confirm import show_scheduler_confirm
from menu.reminders.show_reminder_enter_datetime import show_reminder_enter_datetime
from menu.reminders.show_reminder_enter_recurrence import show_reminder_enter_recurrence
from menu.reminders.show_reminder_confirm import show_reminder_confirm


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    screen = context.user_data.get("current_screen")
    if screen is None:
        return

    user_id = str(update.effective_user.id)
    lang = context.user_data.get("lang", "fr")

    # 1. Modification du message de bienvenue
    if screen == "welcome_edit_message":
        group_id = context.user_data.get("selected_group_id")
        if group_id is None:
            return
        group_id = str(group_id)

        new_text = update.message.text
        persistent = context.bot_data.setdefault("persistent", {})
        user_pdata = persistent.setdefault(user_id, {})
        welcome_config = user_pdata.setdefault("welcome_config", {})
        config = welcome_config.setdefault(group_id, {"enabled": False, "message": "Bienvenue {username} !"})
        config["message"] = new_text
        await save_data(context)
        # Utiliser la clé de succès localisée
        context.user_data["action_success_msg_key"] = "success_welcome_updated"
        await show_welcome_config(update, context)
        return

    # 2. Saisie du texte du message programmé
    elif screen == "scheduler_enter_text":
        new_text = update.message.text
        draft = context.user_data.setdefault("scheduler_draft", {})
        draft["text"] = new_text
        await show_scheduler_enter_interval(update, context)
        return

    # 3. Saisie de l'intervalle (minutes) pour le scheduler
    elif screen == "scheduler_enter_interval":
        draft = context.user_data.setdefault("scheduler_draft", {})
        try:
            interval = int(update.message.text)
        except ValueError:
            interval = None
        if interval is None or interval < MIN_SCHEDULER_INTERVAL:
            # Stocker l'erreur au lieu de l'envoyer séparément
            context.user_data["show_error_msg"] = t("error_interval_minimum", lang)
            await show_scheduler_enter_interval(update, context)
            return
        draft["interval"] = interval
        await show_scheduler_enter_count(update, context)
        return

    # 4. Saisie du nombre d'envois maximum pour le scheduler
    elif screen == "scheduler_enter_count":
        draft = context.user_data.setdefault("scheduler_draft", {})
        try:
            count = int(update.message.text)
        except ValueError:
            count = None
        if count is None or count < 1:
            context.user_data["show_error_msg"] = t("error_count_positive", lang)
            await show_scheduler_enter_count(update, context)
            return
        draft["count"] = count
        await show_scheduler_confirm(update, context)
        return

    # 5. Saisie de la date/heure du rappel
    elif screen == "reminder_enter_datetime":
        user_input = update.message.text.strip()
        try:
            dt = datetime.strptime(user_input, "%Y-%m-%d %H:%M")
            if dt <= datetime.now():
                raise ValueError("date_passee")
        except ValueError:
            context.user_data["show_error_msg"] = t("error_datetime_format", lang)
            await show_reminder_enter_datetime(update, context)
            return

        draft = context.user_data.setdefault("reminder_draft", {})
        draft["datetime"] = dt.isoformat()
        await show_reminder_enter_recurrence(update, context)
        return

    # 6. Saisie du texte du rappel
    elif screen == "reminder_enter_text":
        draft = context.user_data.setdefault("reminder_draft", {})
        draft["text"] = update.message.text
        await show_reminder_confirm(update, context)
        return
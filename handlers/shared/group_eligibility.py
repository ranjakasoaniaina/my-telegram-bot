# handlers/shared/group_eligibility.py

from telegram import Update, ChatMemberRestricted
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from menu.groups.show_group_menu import show_group_list
from menu.scheduler.show_scheduler_select_groups import show_scheduler_select_groups
from menu.reminders.show_reminder_select_groups import show_reminder_select_groups


async def groups_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Vérifie les droits de l'utilisateur et du bot pour chaque groupe connu,
    puis affiche la liste des groupes éligibles.

    Le mode de filtrage est déterminé par context.user_data["group_filter_mode"] :
      - Absent ou "manage" : l'utilisateur doit être admin, le bot admin.
      - "scheduler"       : l'utilisateur doit être membre, le bot membre
                            avec la permission can_send_messages.
      - "reminder"        : identique à "scheduler".
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    bot_id = context.bot.id
    filter_mode = context.user_data.get("group_filter_mode", "manage")

    known_groups = context.bot_data.get("known_groups", {})
    eligible = []

    for chat_id, info in known_groups.items():
        try:
            if filter_mode in ("scheduler", "reminder"):
                # Critères pour les messages programmés et les rappels
                user_member = await context.bot.get_chat_member(chat_id, user_id)
                if user_member.status not in ("member", "administrator", "creator"):
                    continue

                bot_member = await context.bot.get_chat_member(chat_id, bot_id)
                if bot_member.status not in ("member", "administrator", "creator"):
                    continue
                # can_send_messages n'existe que pour les membres restreints.
                # Pour les admins/membres standards, la permission est implicite.
                if isinstance(bot_member, ChatMemberRestricted) and not bot_member.can_send_messages:
                    continue
            else:
                # Critères pour la gestion de groupe (admin / admin)
                user_member = await context.bot.get_chat_member(chat_id, user_id)
                if user_member.status not in ("administrator", "creator"):
                    continue

                bot_member = await context.bot.get_chat_member(chat_id, bot_id)
                if bot_member.status not in ("administrator", "creator"):
                    continue

            eligible.append({
                "id": chat_id,
                "title": info.get("title", f"Groupe {chat_id}")
            })
        except TelegramError:
            continue

    # Stocker la liste et réinitialiser la sélection
    context.user_data["eligible_groups"] = eligible
    context.user_data["selected_group_id"] = None
    context.user_data["selected_group_title"] = None

    # Aiguillage de l'affichage selon le mode
    if filter_mode == "scheduler":
        await show_scheduler_select_groups(update, context)
    elif filter_mode == "reminder":
        await show_reminder_select_groups(update, context)
    else:
        await show_group_list(update, context)
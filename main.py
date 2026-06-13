# trial_bot/main.py

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    MessageHandler,
    filters,
)

from config import TOKEN, OWNER_ID
from storage import load_data

from handlers.trial_middleware import trial_middleware

from handlers.listeners.track_groups import (
    track_my_chat_member,
    track_group_message,
)
from handlers.listeners.welcome_sender import send_welcome_to_new_member
from handlers.listeners.spam_checker import check_spam
from handlers.input_handlers import handle_text_input
from handlers.shared.group_eligibility import groups_entry

from handlers.group_manage.set_config_mode import (
    set_config_mode_welcome,
    set_config_mode_antispam,
    refresh_group_list,
)
from handlers.group_manage.select_group_handler import select_group_handler
from handlers.group_manage.toggle import (
    toggle_welcome,
    toggle_antispam,
    toggle_block_links,
    toggle_block_repeated,
)

from handlers.scheduler.create import (
    enter_new_scheduler,
    toggle_scheduler_group,
    validate_scheduler_groups,
    confirm_create_scheduler,
)
from handlers.scheduler.edit import (
    enter_edit_list,
    select_scheduler_message,
    skip_text,
    skip_interval,
    skip_count,
    confirm_edit_scheduler,
)
from handlers.scheduler.delete import (
    enter_delete_list,
    toggle_delete_message,
    select_all_delete,
    deselect_all_delete,
    confirm_delete_selected,
)

from handlers.reminders.create import (
    set_reminder_mode_private,
    set_reminder_mode_groups,
    toggle_reminder_group,
    validate_reminder_groups,
    set_reminder_recurrence_daily,
    set_reminder_recurrence_weekly,
    set_reminder_recurrence_monthly,
    set_reminder_recurrence_once,
    confirm_reminder_create,
)
from handlers.reminders.edit import (
    enter_edit_reminder,
    select_reminder,
    skip_reminder_datetime,
    skip_reminder_recurrence,
    skip_reminder_text,
    confirm_reminder_edit,
)
from handlers.reminders.delete import (
    enter_delete_reminder,
    toggle_delete_reminder,
    select_all_delete_reminder,
    deselect_all_delete_reminder,
    confirm_delete_reminder,
)

from menu.show_main import show_main
from menu.groups.show_group_menu import show_group_config_choice
from menu.groups.welcome import show_welcome_config, show_welcome_edit_message
from menu.groups.antispam import show_antispam_config
from menu.scheduler.show_scheduler_main import show_scheduler_main
from menu.reminders.show_reminder_main import show_reminder_main
from menu.reminders.show_reminder_enter_mode import show_reminder_enter_mode
from utils import retour

from keep_alive import start_keep_alive


async def post_init(application: Application) -> None:
    """Charge les données persistantes et enregistre l'OWNER_ID."""
    await load_data(application)
    application.bot_data["owner_id"] = OWNER_ID


def main() -> None:
    """Point d'entrée du bot (version essai 3 jours)."""
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    # ==================================================================
    # 0. Middleware de vérification de l'essai (priorité absolue)
    # ==================================================================
    application.add_handler(MessageHandler(filters.ALL, trial_middleware), group=0)
    application.add_handler(CallbackQueryHandler(trial_middleware, pattern=r".*"), group=0)
    application.add_handler(CommandHandler("start", trial_middleware), group=0)

    # ==================================================================
    # 1. Écoute passive des groupes (ne répond jamais)
    # ==================================================================
    application.add_handler(
        ChatMemberHandler(track_my_chat_member, chat_member_types=ChatMemberHandler.MY_CHAT_MEMBER),
        group=1,
    )
    application.add_handler(MessageHandler(filters.ChatType.GROUPS, track_group_message), group=1)
    application.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & filters.StatusUpdate.NEW_CHAT_MEMBERS,
            send_welcome_to_new_member,
        ),
        group=1,
    )
    application.add_handler(
        MessageHandler(filters.ChatType.GROUPS & filters.TEXT, check_spam), group=1
    )

    # ==================================================================
    # 2. Navigation universelle
    # ==================================================================
    application.add_handler(CommandHandler("start", show_main), group=1)
    application.add_handler(CallbackQueryHandler(retour, pattern="^nav:back$"), group=1)
    application.add_handler(CallbackQueryHandler(show_main, pattern="^nav:main$"), group=1)

    # ==================================================================
    # 3. Menu principal
    # ==================================================================
    application.add_handler(
        CallbackQueryHandler(show_group_config_choice, pattern="^menu:group_config_choice$"),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(show_scheduler_main, pattern="^menu:scheduler$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(show_reminder_main, pattern="^menu:reminders$"), group=1
    )

    # ==================================================================
    # 4. Gestion de groupe
    # ==================================================================
    application.add_handler(
        CallbackQueryHandler(set_config_mode_welcome, pattern="^config_mode:welcome$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(set_config_mode_antispam, pattern="^config_mode:antispam$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(refresh_group_list, pattern="^group:refresh$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(select_group_handler, pattern=r"^group:select:"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(show_welcome_config, pattern="^group:welcome$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(show_welcome_edit_message, pattern="^welcome:edit_message$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(toggle_welcome, pattern="^welcome:toggle$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(show_antispam_config, pattern="^group:antispam$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(toggle_antispam, pattern="^antispam:toggle$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(toggle_block_links, pattern="^antispam:block_links$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(toggle_block_repeated, pattern="^antispam:block_repeated$"), group=1
    )

    # ==================================================================
    # 5. Messages programmés
    # ==================================================================
    application.add_handler(
        CallbackQueryHandler(enter_new_scheduler, pattern="^scheduler:new$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(toggle_scheduler_group, pattern=r"^scheduler:toggle_group:"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(validate_scheduler_groups, pattern="^scheduler:groups_validated$"),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(confirm_create_scheduler, pattern="^scheduler:confirm_create$"),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(enter_edit_list, pattern="^scheduler:edit_list$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(select_scheduler_message, pattern=r"^scheduler:select:"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(skip_text, pattern="^scheduler:skip_text$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(skip_interval, pattern="^scheduler:skip_interval$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(skip_count, pattern="^scheduler:skip_count$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(confirm_edit_scheduler, pattern="^scheduler:confirm_edit$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(enter_delete_list, pattern="^scheduler:delete_list$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(toggle_delete_message, pattern=r"^scheduler:delete_toggle:"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(select_all_delete, pattern="^scheduler:delete_select_all$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(deselect_all_delete, pattern="^scheduler:delete_deselect_all$"),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(confirm_delete_selected, pattern="^scheduler:delete_confirm$"),
        group=1,
    )

    # ==================================================================
    # 6. Rappels
    # ==================================================================
    application.add_handler(
        CallbackQueryHandler(show_reminder_enter_mode, pattern="^reminder:new$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(set_reminder_mode_private, pattern="^reminder:mode:private$"),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(set_reminder_mode_groups, pattern="^reminder:mode:groups$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(toggle_reminder_group, pattern=r"^reminder:toggle_group:"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(validate_reminder_groups, pattern="^reminder:groups_validated$"),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(
            set_reminder_recurrence_daily, pattern="^reminder:recurrence:daily$"
        ),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(
            set_reminder_recurrence_weekly, pattern="^reminder:recurrence:weekly$"
        ),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(
            set_reminder_recurrence_monthly, pattern="^reminder:recurrence:monthly$"
        ),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(set_reminder_recurrence_once, pattern="^reminder:recurrence:once$"),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(confirm_reminder_create, pattern="^reminder:confirm_create$"),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(enter_edit_reminder, pattern="^reminder:edit_list$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(select_reminder, pattern=r"^reminder:select:"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(skip_reminder_datetime, pattern="^reminder:skip_datetime$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(skip_reminder_recurrence, pattern="^reminder:skip_recurrence$"),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(skip_reminder_text, pattern="^reminder:skip_text$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(confirm_reminder_edit, pattern="^reminder:confirm_edit$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(enter_delete_reminder, pattern="^reminder:delete_list$"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(toggle_delete_reminder, pattern=r"^reminder:delete_toggle:"), group=1
    )
    application.add_handler(
        CallbackQueryHandler(
            select_all_delete_reminder, pattern="^reminder:delete_select_all$"
        ),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(
            deselect_all_delete_reminder, pattern="^reminder:delete_deselect_all$"
        ),
        group=1,
    )
    application.add_handler(
        CallbackQueryHandler(confirm_delete_reminder, pattern="^reminder:delete_confirm$"),
        group=1,
    )

    # ==================================================================
    # 7. Saisie de texte (toujours en dernier)
    # ==================================================================
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input, block=False),
        group=1,
    )


    #     Lancement du requette http
    # =================================================
    start_keep_alive()

    # ==================================================================
    # Lancement
    # ==================================================================
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
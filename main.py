from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    MessageHandler,
    filters,
)

# ---------- Configuration ----------
from config import TOKEN

# ---------- Stockage persistant ----------
from storage import load_data

# ---------- Écoute silencieuse des groupes ----------
from handlers.listeners.track_groups import (
    track_my_chat_member,
    track_group_message,
)

# ---------- Écoute des nouveaux membres (bienvenue) ----------
from handlers.listeners.welcome_sender import send_welcome_to_new_member

# ---------- Écoute anti‑spam ----------
from handlers.listeners.spam_checker import check_spam

# ---------- Saisie de texte générique ----------
from handlers.input_handlers import handle_text_input

# ---------- Handlers métier pour les groupes (partagés) ----------
from handlers.shared.group_eligibility import groups_entry

# ---------- Handlers métier spécifiques à la gestion de groupe ----------
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

# ---------- Handlers métier pour le scheduler ----------
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

# ---------- Handlers métier pour les rappels ----------
from handlers.reminders.create import (
    set_reminder_mode_private,
    set_reminder_mode_groups,
    toggle_reminder_group,
    validate_reminder_groups,
    set_reminder_recurrence_daily,
    set_reminder_recurrence_weekly,
    set_reminder_recurrence_monthly,
    set_reminder_recurrence_once,          # <-- ajouté
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

# ---------- Handlers pour les statistiques ----------
from handlers.owner_stats import set_stats_period
from menu.stats.show_owner_stats import show_owner_stats

# ---------- Fonctions d'affichage des menus ----------
from menu.show_main import show_main
from menu.groups.show_group_menu import show_group_config_choice
from menu.groups.welcome import show_welcome_config, show_welcome_edit_message
from menu.groups.antispam import show_antispam_config
from menu.scheduler.show_scheduler_main import show_scheduler_main
from menu.reminders.show_reminder_main import show_reminder_main
from menu.reminders.show_reminder_enter_mode import show_reminder_enter_mode

# ---------- Navigation universelle ----------
from utils import retour, owner_only


async def post_init(application: Application) -> None:
    """Charge les données persistantes au démarrage."""
    await load_data(application)


def main() -> None:
    """Point d'entrée du bot."""
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    # ==================================================================
    # 1. Écoute passive des groupes (ne répond jamais)
    # ==================================================================
    application.add_handler(
        ChatMemberHandler(
            track_my_chat_member,
            chat_member_types=ChatMemberHandler.MY_CHAT_MEMBER,
        )
    )
    application.add_handler(
        MessageHandler(filters.ChatType.GROUPS, track_group_message)
    )
    application.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & filters.StatusUpdate.NEW_CHAT_MEMBERS,
            send_welcome_to_new_member
        )
    )
    # Filtre simplifié car check_spam ignore déjà les admins/creator
    application.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & filters.TEXT,
            check_spam
        ),
        group=1
    )

    # ==================================================================
    # 2. Navigation universelle
    # ==================================================================
    application.add_handler(CommandHandler("start", show_main))
    application.add_handler(CallbackQueryHandler(retour, pattern="^nav:back$"))
    application.add_handler(CallbackQueryHandler(show_main, pattern="^nav:main$"))

    # ==================================================================
    # 3. Menu principal
    # ==================================================================
    application.add_handler(
        CallbackQueryHandler(owner_only(show_group_config_choice), pattern="^menu:group_config_choice$")
    )
    application.add_handler(
        CallbackQueryHandler(owner_only(show_scheduler_main), pattern="^menu:scheduler$")
    )
    application.add_handler(
        CallbackQueryHandler(owner_only(show_reminder_main), pattern="^menu:reminders$")
    )

    # ==================================================================
    # 4. Choix du mode de configuration + rafraîchissement
    # ==================================================================
    application.add_handler(
        CallbackQueryHandler(set_config_mode_welcome, pattern="^config_mode:welcome$")
    )
    application.add_handler(
        CallbackQueryHandler(set_config_mode_antispam, pattern="^config_mode:antispam$")
    )
    application.add_handler(
    CallbackQueryHandler(refresh_group_list, pattern="^group:refresh$")
)

    # ==================================================================
    # 5. Sélection d'un groupe dans la liste
    # ==================================================================
    application.add_handler(
        CallbackQueryHandler(select_group_handler, pattern=r"^group:select:")
    )

    # ==================================================================
    # 6. Configuration du message de bienvenue
    # ==================================================================
    application.add_handler(
        CallbackQueryHandler(show_welcome_config, pattern="^group:welcome$")
    )
    application.add_handler(
        CallbackQueryHandler(show_welcome_edit_message, pattern="^welcome:edit_message$")
    )
    application.add_handler(
        CallbackQueryHandler(toggle_welcome, pattern="^welcome:toggle$")
    )

    # ==================================================================
    # 7. Configuration de l'anti‑spam
    # ==================================================================
    application.add_handler(
        CallbackQueryHandler(show_antispam_config, pattern="^group:antispam$")
    )
    application.add_handler(
        CallbackQueryHandler(toggle_antispam, pattern="^antispam:toggle$")
    )
    application.add_handler(
        CallbackQueryHandler(toggle_block_links, pattern="^antispam:block_links$")
    )
    application.add_handler(
        CallbackQueryHandler(toggle_block_repeated, pattern="^antispam:block_repeated$")
    )

    # ==================================================================
    # 8. Messages programmés – création
    # ==================================================================
    application.add_handler(
        CallbackQueryHandler(enter_new_scheduler, pattern="^scheduler:new$")
    )
    application.add_handler(
        CallbackQueryHandler(toggle_scheduler_group, pattern=r"^scheduler:toggle_group:")
    )
    application.add_handler(
        CallbackQueryHandler(validate_scheduler_groups, pattern="^scheduler:groups_validated$")
    )
    application.add_handler(
        CallbackQueryHandler(confirm_create_scheduler, pattern="^scheduler:confirm_create$")
    )

    # ==================================================================
    # 9. Messages programmés – modification
    # ==================================================================
    application.add_handler(
        CallbackQueryHandler(enter_edit_list, pattern="^scheduler:edit_list$")
    )
    application.add_handler(
        CallbackQueryHandler(select_scheduler_message, pattern=r"^scheduler:select:")
    )
    application.add_handler(
        CallbackQueryHandler(skip_text, pattern="^scheduler:skip_text$")
    )
    application.add_handler(
        CallbackQueryHandler(skip_interval, pattern="^scheduler:skip_interval$")
    )
    application.add_handler(
        CallbackQueryHandler(skip_count, pattern="^scheduler:skip_count$")
    )
    application.add_handler(
        CallbackQueryHandler(confirm_edit_scheduler, pattern="^scheduler:confirm_edit$")
    )

    # ==================================================================
    # 10. Messages programmés – suppression
    # ==================================================================
    application.add_handler(CallbackQueryHandler(enter_delete_list, pattern="^scheduler:delete_list$"))
    application.add_handler(CallbackQueryHandler(toggle_delete_message, pattern=r"^scheduler:delete_toggle:"))
    application.add_handler(CallbackQueryHandler(select_all_delete, pattern="^scheduler:delete_select_all$"))
    application.add_handler(CallbackQueryHandler(deselect_all_delete, pattern="^scheduler:delete_deselect_all$"))
    application.add_handler(CallbackQueryHandler(confirm_delete_selected, pattern="^scheduler:delete_confirm$"))

    # ==================================================================
    # 11. Rappels – création
    # ==================================================================
    application.add_handler(CallbackQueryHandler(show_reminder_enter_mode, pattern="^reminder:new$"))
    application.add_handler(CallbackQueryHandler(set_reminder_mode_private, pattern="^reminder:mode:private$"))
    application.add_handler(CallbackQueryHandler(set_reminder_mode_groups, pattern="^reminder:mode:groups$"))
    application.add_handler(CallbackQueryHandler(toggle_reminder_group, pattern=r"^reminder:toggle_group:"))
    application.add_handler(CallbackQueryHandler(validate_reminder_groups, pattern="^reminder:groups_validated$"))
    application.add_handler(CallbackQueryHandler(set_reminder_recurrence_daily, pattern="^reminder:recurrence:daily$"))
    application.add_handler(CallbackQueryHandler(set_reminder_recurrence_weekly, pattern="^reminder:recurrence:weekly$"))
    application.add_handler(CallbackQueryHandler(set_reminder_recurrence_monthly, pattern="^reminder:recurrence:monthly$"))
    application.add_handler(CallbackQueryHandler(set_reminder_recurrence_once, pattern="^reminder:recurrence:once$"))
    application.add_handler(CallbackQueryHandler(confirm_reminder_create, pattern="^reminder:confirm_create$"))

    # ==================================================================
    # 12. Rappels – modification
    # ==================================================================
    application.add_handler(CallbackQueryHandler(enter_edit_reminder, pattern="^reminder:edit_list$"))
    application.add_handler(CallbackQueryHandler(select_reminder, pattern=r"^reminder:select:"))
    application.add_handler(CallbackQueryHandler(skip_reminder_datetime, pattern="^reminder:skip_datetime$"))
    application.add_handler(CallbackQueryHandler(skip_reminder_recurrence, pattern="^reminder:skip_recurrence$"))
    application.add_handler(CallbackQueryHandler(skip_reminder_text, pattern="^reminder:skip_text$"))
    application.add_handler(CallbackQueryHandler(confirm_reminder_edit, pattern="^reminder:confirm_edit$"))

    # ==================================================================
    # 13. Rappels – suppression
    # ==================================================================
    application.add_handler(CallbackQueryHandler(enter_delete_reminder, pattern="^reminder:delete_list$"))
    application.add_handler(CallbackQueryHandler(toggle_delete_reminder, pattern=r"^reminder:delete_toggle:"))
    application.add_handler(CallbackQueryHandler(select_all_delete_reminder, pattern="^reminder:delete_select_all$"))
    application.add_handler(CallbackQueryHandler(deselect_all_delete_reminder, pattern="^reminder:delete_deselect_all$"))
    application.add_handler(CallbackQueryHandler(confirm_delete_reminder, pattern="^reminder:delete_confirm$"))

    # ==================================================================
    # 14. Statistiques
    # ==================================================================
    application.add_handler(CallbackQueryHandler(show_owner_stats, pattern="^owner:stats$"))
    application.add_handler(CallbackQueryHandler(set_stats_period, pattern=r"^stats:period:"))

    # ==================================================================
    # 15. Saisie de texte (toujours en dernier pour éviter les conflits)
    # ==================================================================
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input, block=False)
    )

    # ==================================================================
    # Lancement
    # ==================================================================
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
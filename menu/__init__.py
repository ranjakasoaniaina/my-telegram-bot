# menu/__init__.py

from menu.show_main import show_main
from menu.groups.show_group_menu import show_group_config_choice, show_group_list
from menu.groups.welcome import show_welcome_config, show_welcome_edit_message
from menu.groups.antispam import show_antispam_config
from menu.scheduler.show_scheduler_main import show_scheduler_main
from menu.scheduler.show_scheduler_select_groups import show_scheduler_select_groups
from menu.scheduler.show_scheduler_enter_text import show_scheduler_enter_text
from menu.scheduler.show_scheduler_enter_interval import show_scheduler_enter_interval
from menu.scheduler.show_scheduler_enter_count import show_scheduler_enter_count
from menu.scheduler.show_scheduler_confirm import show_scheduler_confirm
from menu.scheduler.show_scheduler_edit_list import show_scheduler_edit_list
from menu.scheduler.show_scheduler_delete_list import show_scheduler_delete_list
from menu.reminders.show_reminder_main import show_reminder_main
from menu.reminders.show_reminder_enter_mode import show_reminder_enter_mode
from menu.reminders.show_reminder_select_groups import show_reminder_select_groups
from menu.reminders.show_reminder_enter_datetime import show_reminder_enter_datetime
from menu.reminders.show_reminder_enter_recurrence import show_reminder_enter_recurrence
from menu.reminders.show_reminder_enter_text import show_reminder_enter_text
from menu.reminders.show_reminder_confirm import show_reminder_confirm
from menu.reminders.show_reminder_edit_list import show_reminder_edit_list
from menu.reminders.show_reminder_delete_list import show_reminder_delete_list


SCREENS = {
    "main": show_main,
    "group_config_choice": show_group_config_choice,
    "group_list": show_group_list,
    "welcome_config": show_welcome_config,
    "welcome_edit_message": show_welcome_edit_message,
    "antispam_config": show_antispam_config,
    "scheduler_main": show_scheduler_main,
    "scheduler_select_groups": show_scheduler_select_groups,
    "scheduler_enter_text": show_scheduler_enter_text,
    "scheduler_enter_interval": show_scheduler_enter_interval,
    "scheduler_enter_count": show_scheduler_enter_count,
    "scheduler_confirm": show_scheduler_confirm,
    "scheduler_edit_list": show_scheduler_edit_list,
    "scheduler_delete_list": show_scheduler_delete_list,
    "reminder_main": show_reminder_main,
    "reminder_enter_mode": show_reminder_enter_mode,
    "reminder_select_groups": show_reminder_select_groups,
    "reminder_enter_datetime": show_reminder_enter_datetime,
    "reminder_enter_recurrence": show_reminder_enter_recurrence,
    "reminder_enter_text": show_reminder_enter_text,
    "reminder_confirm": show_reminder_confirm,
    "reminder_edit_list": show_reminder_edit_list,
    "reminder_delete_list": show_reminder_delete_list,
}
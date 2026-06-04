# menu/show_main.py

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import OWNER_ID, DEMO_CHANNEL_FR, DEMO_CHANNEL_EN, CONTACT_URL, APP_MODE
from storage import save_data
from texts import t
from menu.display_utils import estimate_width, pad_to_width


async def show_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le menu principal (édite le message actif ou envoie le premier)."""

    is_owner = update.effective_user.id == OWNER_ID

    # 1. Langue
    detected = update.effective_user.language_code or "en"
    context.user_data["lang"] = "fr" if detected.startswith("fr") else "en"
    lang = context.user_data["lang"]

    # 2. Accès refusé en mode client pour les non‑propriétaires
    if APP_MODE == "client" and not is_owner:
        return

    # 3. Construction du texte et du clavier
    if APP_MODE == "personal" and not is_owner:
        # ---------- Vitrine ----------
        demo_url = DEMO_CHANNEL_FR if lang == "fr" else DEMO_CHANNEL_EN
        texte = t("showcase_welcome", lang)

        labels = [
            t("main_menu_group_mgmt", lang).replace("👥 ", ""),
            t("main_menu_scheduled", lang).replace("📅 ", ""),
            t("main_menu_reminders", lang).replace("⏰ ", ""),
        ]
        callbacks = [
            "menu:group_config_choice",
            "menu:scheduler",
            "menu:reminders",
        ]

        widths = [estimate_width(l) for l in labels]
        target_width = max(widths)
        padded_labels = [pad_to_width(l, target_width) for l in labels]

        boutons = []
        for padded_label, cb in zip(padded_labels, callbacks):
            boutons.append([InlineKeyboardButton(f"🔒 {padded_label}", callback_data=cb)])

        boutons.append([InlineKeyboardButton(t("showcase_demo", lang), url=demo_url)])
        boutons.append([InlineKeyboardButton(t("showcase_contact", lang), url=CONTACT_URL)])

        # ----- Compteur de /start (visiteur uniquement) -----
        stats = context.bot_data.setdefault("persistent", {}).setdefault("vitrine_stats", {})
        today = datetime.now().strftime("%Y-%m-%d")
        daily = stats.setdefault("daily", {})
        day_data = daily.setdefault(today, {"unique_visitors": {}, "starts": 0})
        user_id = str(update.effective_user.id)
        day_data["unique_visitors"][user_id] = True
        day_data["starts"] = day_data.get("starts", 0) + 1
        stats.setdefault("unique_visitors_global", {})[user_id] = True
        stats["total_starts"] = stats.get("total_starts", 0) + 1
        await save_data(context)

    else:
        # ---------- Menu propriétaire (client ou personnel) ----------
        texte = t("main_menu_welcome", lang)
        boutons = [
            [InlineKeyboardButton(t("main_menu_group_mgmt", lang), callback_data="menu:group_config_choice")],
            [InlineKeyboardButton(t("main_menu_scheduled", lang), callback_data="menu:scheduler")],
            [InlineKeyboardButton(t("main_menu_reminders", lang), callback_data="menu:reminders")],
        ]
        # Bouton Statistiques uniquement en mode personnel
        if APP_MODE == "personal":
            boutons.append([InlineKeyboardButton(t("main_menu_stats", lang), callback_data="owner:stats")])

    clavier = InlineKeyboardMarkup(boutons)

    context.user_data["current_screen"] = "main"
    context.user_data["step_parent"] = None
    context.user_data["menu_parent"] = None

    # 4. Affichage unique
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        chat_id = update.effective_chat.id
        old_message_id = context.user_data.get("active_message_id")
        if old_message_id:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=old_message_id)
            except Exception:
                pass
        message = await context.bot.send_message(chat_id=chat_id, text=texte, reply_markup=clavier)
        context.user_data["active_message_id"] = message.message_id
# menu/stats/show_owner_stats.py

from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import t

PERIOD_DAILY = "daily"
PERIOD_WEEKLY = "weekly"
PERIOD_MONTHLY = "monthly"


def _compute_stats(stats: dict, period: str, reference_date=None):
    """
    Retourne un tuple (visiteurs_uniques, visiteurs_intéressés, démarrages, clics_totaux).
    """
    if reference_date is None:
        reference_date = datetime.now()

    daily = stats.get("daily", {})
    if period == PERIOD_DAILY:
        day_str = reference_date.strftime("%Y-%m-%d")
        day_data = daily.get(day_str, {})
        visitors = len(day_data.get("unique_visitors", {}))
        interested = len(day_data.get("clicking_visitors", {}))
        starts = day_data.get("starts", 0)
        clicks = day_data.get("clicks_reserved", 0)
        return visitors, interested, starts, clicks

    if period == PERIOD_WEEKLY:
        return _aggregate_period(stats, 7, reference_date)

    if period == PERIOD_MONTHLY:
        return _aggregate_period(stats, 30, reference_date)

    return 0, 0, 0, 0


def _aggregate_period(stats: dict, days: int, reference_date):
    """Agrège les données sur `days` jours glissants."""
    daily = stats.get("daily", {})
    visitor_ids = set()
    interested_ids = set()
    total_starts = 0
    total_clicks = 0
    for i in range(days):
        day = reference_date - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        day_data = daily.get(day_str, {})
        for uid in day_data.get("unique_visitors", {}):
            visitor_ids.add(uid)
        for uid in day_data.get("clicking_visitors", {}):
            interested_ids.add(uid)
        total_starts += day_data.get("starts", 0)
        total_clicks += day_data.get("clicks_reserved", 0)
    return len(visitor_ids), len(interested_ids), total_starts, total_clicks


def _compute_previous_period(stats: dict, period: str, reference_date=None):
    """Décale la date de référence pour obtenir la période précédente."""
    if reference_date is None:
        reference_date = datetime.now()
    if period == PERIOD_DAILY:
        previous_date = reference_date - timedelta(days=1)
        return _compute_stats(stats, period, previous_date)
    if period == PERIOD_WEEKLY:
        previous_date = reference_date - timedelta(weeks=1)
        return _compute_stats(stats, period, previous_date)
    if period == PERIOD_MONTHLY:
        previous_date = reference_date - timedelta(days=30)
        return _compute_stats(stats, period, previous_date)
    return 0, 0, 0, 0


async def show_owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche les statistiques avec comparaisons (aujourd'hui/hier, semaine, mois)."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get("lang", "fr")
    period = context.user_data.get("stats_period", PERIOD_DAILY)

    stats = context.bot_data.get("persistent", {}).get("vitrine_stats", {})

    visitors, interested, starts, clicks = _compute_stats(stats, period)
    prev_visitors, prev_interested, prev_starts, _ = _compute_previous_period(stats, period)

    # Taux d'intérêt (plafonné à 100 %)
    interest_rate = (interested / visitors * 100) if visitors > 0 else 0.0
    prev_interest_rate = (prev_interested / prev_visitors * 100) if prev_visitors > 0 else 0.0

    period_label_key = {
        PERIOD_DAILY: "stats_period_daily",
        PERIOD_WEEKLY: "stats_period_weekly",
        PERIOD_MONTHLY: "stats_period_monthly",
    }.get(period, "stats_period_daily")

    period_label = t(period_label_key, lang)

    texte = (
        t("stats_title", lang, period=period_label) + "\n\n"
        + t("stats_starts", lang, starts=starts, prev_starts=prev_starts) + "\n"
        + t("stats_visitors", lang, visitors=visitors, prev_visitors=prev_visitors) + "\n"
        + t("stats_interested", lang, interested=interested, prev_interested=prev_interested) + "\n"
        + t("stats_interest_rate", lang, rate=f"{interest_rate:.1f}", prev_rate=f"{prev_interest_rate:.1f}") + "\n\n"
        + t("stats_compare", lang)
    )

    # Construction des boutons de bascule (on n'affiche que ceux qui ne correspondent pas à la période courante)
    boutons_ligne = []
    if period != PERIOD_WEEKLY:
        boutons_ligne.append(
            InlineKeyboardButton(t("stats_btn_weekly", lang), callback_data="stats:period:weekly")
        )
    if period != PERIOD_MONTHLY:
        boutons_ligne.append(
            InlineKeyboardButton(t("stats_btn_monthly", lang), callback_data="stats:period:monthly")
        )
    if period != PERIOD_DAILY:
        boutons_ligne.append(
            InlineKeyboardButton(t("stats_btn_daily", lang), callback_data="stats:period:daily")
        )

    clavier = InlineKeyboardMarkup([
        boutons_ligne,
        [InlineKeyboardButton(t("back", lang), callback_data="nav:back")]
    ])

    context.user_data["current_screen"] = "owner_stats"
    context.user_data["step_parent"] = "main"
    context.user_data["menu_parent"] = "main"

    if query:
        await query.edit_message_text(text=texte, reply_markup=clavier)
    else:
        chat_id = update.effective_chat.id
        message_id = context.user_data.get("active_message_id")
        if message_id:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id, message_id=message_id,
                    text=texte, reply_markup=clavier
                )
            except Exception:
                if update.message:
                    msg = await update.message.reply_text(text=texte, reply_markup=clavier)
                else:
                    msg = await context.bot.send_message(chat_id=chat_id, text=texte, reply_markup=clavier)
                context.user_data["active_message_id"] = msg.message_id
        else:
            if update.message:
                msg = await update.message.reply_text(text=texte, reply_markup=clavier)
            else:
                msg = await context.bot.send_message(chat_id=chat_id, text=texte, reply_markup=clavier)
            context.user_data["active_message_id"] = msg.message_id
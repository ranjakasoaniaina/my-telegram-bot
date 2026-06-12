# menu/display_utils.py
import unicodedata
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
# Table ultra-détaillée des largeurs de caractères (unité relative, 1.0 ≈ largeur chiffre)
CHAR_WIDTH_TABLE = {
    # minuscules
    'i':0.30, 'l':0.30,
    't':0.40,
    'r':0.45, 'f':0.45, 'j':0.45,
    'a':0.55, 'c':0.55, 'e':0.55, 'g':0.55, 'k':0.55, 'o':0.55,
    's':0.55, 'u':0.55, 'v':0.55, 'x':0.55, 'z':0.55, 'n':0.55,
    'b':0.60, 'd':0.60, 'h':0.60, 'p':0.60, 'q':0.60, 'y':0.60,
    'm':0.85, 'w':0.90,
    # majuscules
    'I':0.35, 'J':0.50, 'L':0.55, 'T':0.60,
    'A':0.70, 'B':0.70, 'C':0.70, 'D':0.70, 'E':0.70, 'F':0.70,
    'G':0.70, 'H':0.70, 'K':0.70, 'N':0.70, 'O':0.70, 'P':0.70,
    'Q':0.70, 'R':0.70, 'S':0.70, 'U':0.70, 'V':0.70, 'X':0.70,
    'Y':0.70, 'Z':0.70,
    'M':1.05, 'W':1.10,
    # chiffres
    '1':0.45,
    '2':0.55, '3':0.55, '4':0.55, '5':0.55, '6':0.55,
    '7':0.55, '8':0.55, '9':0.55, '0':0.55,
    # ponctuations / symboles
    ' ':0.30, "'":0.30, '.':0.30, ',':0.30, '!':0.30, ':':0.30,
    ';':0.30, '?':0.30,
    '"':0.35, '\u201c':0.35, '\u201d':0.35, '\u2018':0.35, '\u2019':0.35,
    '(':0.40, ')':0.40, '[':0.40, ']':0.40, '{':0.40, '}':0.40,
    '/':0.40, '\\':0.40,
    '-':0.50, '\u2013':0.50, '\u2014':0.50, '_':0.50,
    '*':0.55, '+':0.55, '=':0.55, '<':0.55, '>':0.55, '|':0.55,
    '@':0.85, '&':0.75, '#':0.70, '%':0.80, '\u2030':0.80,
    '$':0.70, '€':0.70, '£':0.70, '¥':0.70,
    '^':0.40, '~':0.40, '`':0.40,
}

def _base_char(c):
    """Retourne le caractère de base sans diacritique."""
    decomposed = unicodedata.normalize('NFKD', c)
    return decomposed[0] if decomposed else c

def estimate_width(text: str) -> float:
    """Estime la largeur visuelle d'un texte (unité arbitraire)."""
    total = 0.0
    for c in text:
        if unicodedata.category(c) == "So":      # emoji / symbole
            total += 1.10
            continue
        if c in CHAR_WIDTH_TABLE:
            total += CHAR_WIDTH_TABLE[c]
        else:
            base = _base_char(c)
            if base in CHAR_WIDTH_TABLE:
                total += CHAR_WIDTH_TABLE[base]
            elif c.isupper():
                total += 0.70
            elif c.isdigit():
                total += 0.55
            else:
                total += 0.55   # fallback
    return total

# Espaces Unicode à chasse fixe utilisés pour le remplissage (du plus large au plus fin)
FILLER_SPACES = [
    ("\u2003", 1.0),   # Em Space
    ("\u2002", 0.5),    # En Space
    ("\u2007", 0.55),   # Figure Space (largeur chiffre)
    ("\u2009", 0.2),    # Thin Space
    ("\u200A", 0.1),    # Hair Space
]

def pad_to_width(text: str, target_width: float) -> str:
    """Ajoute des espaces Unicode pour que la largeur estimée atteigne target_width."""
    current = estimate_width(text)
    missing = target_width - current
    if missing <= 0:
        return text
    for space_char, space_width in FILLER_SPACES:
        count = int(missing // space_width)
        text += space_char * count
        missing -= count * space_width
    if missing > 0.05:          # résidu
        text += "\u200A"        # Hair Space
    return text







async def display_message(update, context, texte, clavier):
    # Si on a un callback, on édite le message d’origine (navigation par bouton)
    if update.callback_query:
        query = update.callback_query
        await query.edit_message_text(text=texte, reply_markup=clavier)
        return

    # Pas de callback → on supprime l’ancien message et on envoie un nouveau en bas
    chat_id = update.effective_chat.id
    old_message_id = context.user_data.get("active_message_id")

    # 1. Supprimer l’ancien message s’il existe
    if old_message_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=old_message_id)
        except Exception:
            pass  # déjà supprimé ou introuvable

    # 2. Envoyer un nouveau message (il apparaîtra en bas)
    if update.message:
        message = await update.message.reply_text(text=texte, reply_markup=clavier)
    else:
        message = await context.bot.send_message(chat_id=chat_id, text=texte, reply_markup=clavier)

    # 3. Mettre à jour l’ID du message actif
    context.user_data["active_message_id"] = message.message_id
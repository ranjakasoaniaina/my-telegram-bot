import asyncio
import json
import os
import tempfile
from telegram.ext import ContextTypes

# Le fichier où toutes les données persistantes seront stockées
DATA_FILE = "user_data.json"

# Verrou asynchrone pour empêcher les écritures concurrentes
_lock = asyncio.Lock()


async def load_data(context: ContextTypes.DEFAULT_TYPE) -> dict:
    """
    Charge les données depuis le fichier JSON et les place dans
    context.bot_data['persistent'].
    Si le fichier n'existe pas, il est créé automatiquement avec un
    dictionnaire vide.
    """
    # Création automatique du fichier s'il n'existe pas
    if not os.path.exists(DATA_FILE):
        async with _lock:
            # Double vérification après acquisition du verrou
            if not os.path.exists(DATA_FILE):
                with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", delete=False, dir="."
                ) as tmp:
                    json.dump({}, tmp, indent=2, ensure_ascii=False)
                    tmp.flush()
                    os.fsync(tmp.fileno())
                os.replace(tmp.name, DATA_FILE)

    # Lecture des données
    async with _lock:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    context.bot_data["persistent"] = data
    return data


async def save_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sauvegarde le contenu de context.bot_data['persistent'] dans le
    fichier JSON de manière atomique (écriture dans un fichier
    temporaire puis remplacement).
    """
    data = context.bot_data.get("persistent", {})
    async with _lock:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False, dir="."
        ) as tmp:
            json.dump(data, tmp, indent=2, ensure_ascii=False)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp.name, DATA_FILE)
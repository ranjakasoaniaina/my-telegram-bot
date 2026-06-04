import os

TOKEN = os.getenv("BOT_TOKEN", "8681736416:AAE1H-6z1cqe-zwfi2Qg_z-8R6jsk6vNJFY")
OWNER_ID = int(os.getenv("OWNER_ID", "8700808348"))
APP_MODE = os.getenv("APP_MODE", "personal")
MIN_SCHEDULER_INTERVAL = int(os.getenv("MIN_SCHEDULER_INTERVAL", "10"))
MAX_SCHEDULER_DURATION_MINUTES = int(os.getenv("MAX_SCHEDULER_DURATION_MINUTES", "1440"))
TIMEZONE_OFFSET = os.getenv("TIMEZONE_OFFSET", "+03:00")
DEMO_CHANNEL_FR = os.getenv("DEMO_CHANNEL_FR", "https://t.me/DevSculptChannel")
DEMO_CHANNEL_EN = os.getenv("DEMO_CHANNEL_EN", "https://t.me/DevSculptChannel")
CONTACT_URL = os.getenv("CONTACT_URL", "https://t.me/DevSculpt")
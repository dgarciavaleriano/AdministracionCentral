# ACFrontEnd/config/settings.py
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8080")
API_TIMEOUT = float(os.getenv("API_TIMEOUT", "10"))
NICEGUI_STORAGE_SECRET = os.getenv('NICEGUI_STORAGE_SECRET', 'dev-insecure-change-me')
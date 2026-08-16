#!/usr/bin/env python3
"""
Administración Central (AC) - Punto de entrada principal
"""

from nicegui import ui
from utils.constants import APP_TITLE
import os

@ui.page('/')
def landing():
    """Página de inicio"""
    from pages.landing import create_landing_page
    create_landing_page()

@ui.page('/login')
def login():
    """Página de login"""
    from pages.login import create_login_page
    create_login_page()

@ui.page('/dashboard')
def dashboard():
    """Dashboard principal"""
    from pages.dashboard import create_dashboard_page
    create_dashboard_page()

if __name__ in {'__main__', '__mp_main__'}:
    API_BASE_URL = os.getenv("API_BASE_URL")
    NICEGUI_STORAGE_SECRET = os.getenv('NICEGUI_STORAGE_SECRET')
    ui.run(
        title=APP_TITLE,
        favicon='🏛️',
        language='es',
        storage_secret=NICEGUI_STORAGE_SECRET,
        port=8000,
    )
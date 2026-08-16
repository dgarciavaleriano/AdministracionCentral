#!/usr/bin/env python3
"""
Administración Central (AC) - Punto de entrada principal
"""

from nicegui import ui
from dotenv import load_dotenv
from utils.constants import APP_TITLE
import os

load_dotenv()

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
    storage_secret = os.getenv('NICEGUI_STORAGE_SECRET')
    if not storage_secret:
        import warnings
        warnings.warn(
            "NICEGUI_STORAGE_SECRET no está configurado. "
            "Crea un fichero ui/.env con NICEGUI_STORAGE_SECRET=<secreto> antes de arrancar.",
            stacklevel=1,
        )
    ui.run(
        title=APP_TITLE,
        favicon='🏛️',
        language='es',
        storage_secret=storage_secret,
        port=8000,
    )
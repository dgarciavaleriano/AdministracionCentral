#!/usr/bin/env python3
"""
Administración Central (AC) - Punto de entrada principal
"""

from nicegui import ui

from config.settings import SECRETOS_PUBLICOS, settings
from utils.constants import APP_TITLE

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
    if settings.nicegui_storage_secret in SECRETOS_PUBLICOS:
        import warnings
        warnings.warn(
            "NICEGUI_STORAGE_SECRET tiene un valor que está publicado en el "
            "repositorio, así que no firma nada: vale para trabajar en local, "
            "pero define uno propio en ui/.env (o en el entorno) antes de desplegar.",
            stacklevel=1,
        )
    ui.run(
        title=APP_TITLE,
        favicon='🏛️',
        language='es',
        storage_secret=settings.nicegui_storage_secret,
        host=settings.ui_host,
        port=settings.ui_port,
    )

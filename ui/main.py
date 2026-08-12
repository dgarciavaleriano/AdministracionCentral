#!/usr/bin/env python3
"""
Administración Central (AC) - Punto de entrada principal
"""

from nicegui import ui, app
from utils.constants import APP_TITLE

# Inicializar tema al arrancar
@app.on_startup
def startup():
    """Inicializa el tema al arrancar la aplicación"""
    # Recuperar preferencia de localStorage
    pass

@ui.page('/')
def landing():
    """Página de inicio"""
    from pages.landing import create_landing_page
    from utils.themes import init_dark_mode
    dark_mode = init_dark_mode()  # Inicializar con preferencia guardada
    create_landing_page()

@ui.page('/login')
def login():
    """Página de login"""
    from pages.login import create_login_page
    from utils.themes import init_dark_mode
    dark_mode = init_dark_mode()  # Inicializar con preferencia guardada
    create_login_page()

@ui.page('/dashboard')
def dashboard():
    """Dashboard principal"""
    from pages.dashboard import create_dashboard_page
    from utils.themes import init_dark_mode
    dark_mode = init_dark_mode()  # Inicializar con preferencia guardada
    create_dashboard_page()

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        title=APP_TITLE,
        favicon='🏛️',
        language='es',
        storage_secret='ac-secret-key-2024',
        port=8000,
    )
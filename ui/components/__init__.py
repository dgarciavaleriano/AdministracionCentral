#!/usr/bin/env python3
from nicegui import ui, app
from utils.constants import APP_TITLE
from pages.landing import create_landing_page
from pages.login import create_login_page
from pages.dashboard import create_dashboard_page
from utils.themes import init_theme

# Inicializar tema global
dark_mode = ui.dark_mode()

@ui.page('/')
def landing():
    """Página de inicio/Landing"""
    create_landing_page()

@ui.page('/login')
def login():
    """Página de login"""
    create_login_page()

@ui.page('/dashboard')
def dashboard():
    """Página principal del dashboard"""
    create_dashboard_page()

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        title=APP_TITLE,
        favicon='🏛️',
        language='es',
        storage_secret='ac-secret-key-2024',  # Necesario para almacenamiento
    )
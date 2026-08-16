"""Gestión de temas claro/oscuro"""

from nicegui import ui, app

LIGHT_THEME = {
    'primary': '#1a73e8',
    'secondary': '#34a853',
    'bg': '#f8f9fa',
    'sidebar_bg': '#ffffff',
    'chat_bg': '#ffffff',
    'card_bg': '#ffffff',
    'text': '#1f2937',
    'text_secondary': '#6b7280',
    'border': '#e5e7eb',
    'hover': '#f3f4f6',
    'badge_bg': 'rgba(255,255,255,0.2)',
}

DARK_THEME = {
    'primary': '#4285f4',
    'secondary': '#34a853',
    'bg': '#0f172a',
    'sidebar_bg': '#1e293b',
    'chat_bg': '#1e293b',
    'card_bg': '#1e293b',
    'text': '#e2e8f0',
    'text_secondary': '#94a3b8',
    'border': '#334155',
    'hover': '#334155',
    'badge_bg': 'rgba(255,255,255,0.15)',
}

def get_theme_colors(dark: bool = False) -> dict:
    """Obtiene los colores del tema actual"""
    return DARK_THEME if dark else LIGHT_THEME

def get_theme_css_rules(dark: bool = False) -> str:
    """Genera las reglas CSS del tema (sin etiquetas <style>)"""
    theme = get_theme_colors(dark)

    return f'''
            body {{ 
                background-color: {theme['bg']} !important;
                color: {theme['text']} !important;
            }}
            
            .gradient-header {{
                background: linear-gradient(135deg, {theme['primary']}, {theme['secondary']});
            }}
            
            .sidebar {{ 
                background: {theme['sidebar_bg']} !important; 
                border-right: 1px solid {theme['border']} !important;
            }}
            
            .chat-container {{ 
                background: {theme['chat_bg']} !important; 
                border-radius: 16px;
                border: 1px solid {theme['border']} !important;
            }}
            
            .message-input {{ 
                border: 2px solid {theme['border']} !important;
                border-radius: 24px !important;
                background: {theme['bg']} !important;
                color: {theme['text']} !important;
            }}
            
            .message-input:focus {{
                border-color: {theme['primary']} !important;
                box-shadow: 0 0 0 3px rgba(66,133,244,0.1) !important;
            }}
            
            .tramite-card {{
                transition: all 0.3s ease;
                cursor: pointer;
                border-radius: 12px;
                padding: 12px;
                margin: 4px 0;
            }}
            
            .tramite-card:hover {{
                background: {theme['hover']} !important;
                transform: translateX(4px);
            }}
            
            .message-bubble-own {{
                background: {theme['primary']}15 !important;
                border: 1px solid {theme['primary']}30 !important;
            }}
            
            .message-bubble-other {{
                background: {theme['hover']} !important;
                border: 1px solid {theme['border']} !important;
            }}
            
            .theme-toggle {{
                cursor: pointer;
                padding: 8px;
                border-radius: 12px;
                transition: all 0.3s ease;
                color: #ffffff !important;
            }}
            
            .theme-toggle:hover {{
                background: rgba(255,255,255,0.2) !important;
            }}
            
            .white-text {{
                color: #ffffff !important;
            }}
            
            .badge-glass {{
                background: {theme['badge_bg']} !important;
                backdrop-filter: blur(10px);
                color: #ffffff !important;
            }}
            
            .profile-btn {{
                color: #ffffff !important;
                background: rgba(255,255,255,0.2) !important;
            }}
            
            .profile-btn:hover {{
                background: rgba(255,255,255,0.3) !important;
            }}
            
            .gradient-header .q-btn {{
                color: #ffffff !important;
            }}

            .chat-header-theme-toggle .theme-toggle,
            .chat-header-theme-toggle .white-text {{
                color: {theme['text']} !important;
            }}

            .chat-header-theme-toggle .theme-toggle:hover {{
                background: {theme['hover']} !important;
            }}
            
            .login-container {{
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 100% !important;
                min-height: calc(100vh - 64px) !important;
                padding: 20px !important;
                box-sizing: border-box !important;
            }}

            .login-container .q-card {{
                margin: 0 auto !important;
            }}
            
            ::-webkit-scrollbar {{
                width: 6px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: {theme['bg']};
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: {theme['border']};
                border-radius: 3px;
            }}
    '''

def get_theme_css(dark: bool = False) -> str:
    """Genera CSS dinámico según el tema"""
    return f'''
        <style>
{get_theme_css_rules(dark)}        </style>
    '''

def init_dark_mode():
    """Inicializa el modo oscuro desde almacenamiento"""
    dark = ui.dark_mode()
    # Recuperar preferencia guardada
    saved = app.storage.user.get('dark_mode', False)
    if saved:
        dark.enable()
    else:
        dark.disable()
    return dark

def toggle_theme(dark_mode):
    """Cambia el tema y guarda preferencia"""
    # Cambiar el valor
    if dark_mode.value:
        dark_mode.disable()
    else:
        dark_mode.enable()

    # Guardar preferencia
    app.storage.user['dark_mode'] = dark_mode.value

    # Notificar
    ui.notify(
        '🌙 Modo oscuro activado' if dark_mode.value else '☀️ Modo claro activado',
        position='top-right',
        timeout=2000
    )

    # Actualizar CSS dinámicamente sin recargar la página
    css_rules = get_theme_css_rules(dark_mode.value)
    ui.run_javascript(f'''
        (function() {{
            var existing = document.getElementById('nicegui-theme-dynamic');
            if (existing) {{ existing.remove(); }}
            var style = document.createElement('style');
            style.id = 'nicegui-theme-dynamic';
            style.textContent = {repr(css_rules)};
            document.head.appendChild(style);
        }})();
    ''')

@ui.refreshable
def create_theme_toggle(dark_mode):
    """Crea un botón de toggle de tema"""
    def handle_click():
        toggle_theme(dark_mode)
        create_theme_toggle.refresh()

    with ui.element('div').classes('theme-toggle') as theme_btn:
        icon_name = 'dark_mode' if not dark_mode.value else 'light_mode'
        ui.icon(icon_name).classes('text-lg white-text')
        next_mode = 'modo claro' if dark_mode.value else 'modo oscuro'
        theme_btn.tooltip(f'Cambiar a {next_mode}')
        theme_btn.on('click', handle_click)
    return theme_btn

"""Landing page de la aplicación"""

from nicegui import ui, run
from utils.constants import APP_TITLE, APP_VERSION, APP_DESCRIPTION
from utils.themes import get_theme_css, create_theme_toggle, init_dark_mode
from services.api.endpoints.users import users_api

async def probar_api():
    try:
        result = await run.io_bound(users_api.hello_world)
        ui.notify(f"API responde: {result}", type="positive")
    except Exception:
        __import__('logging').getLogger(__name__).exception('Error llamando API')
        ui.notify('No se pudo contactar con el API en este momento.', type='negative')

def create_landing_page():
    """Crea la landing page"""
    dark_mode = init_dark_mode()
    ui.add_head_html(get_theme_css(dark_mode.value))
    
    # Header
    with ui.header().classes('gradient-header text-white'):
        with ui.row().classes('w-full max-w-7xl mx-auto items-center justify-between p-4'):
            with ui.row().classes('items-center gap-3'):
                ui.icon('account_balance', size='2rem').classes('white-text')
                ui.label(APP_TITLE).classes('text-2xl font-bold white-text')
            
            with ui.row().classes('gap-4 items-center'):
                ui.chip(
                    'Modo oscuro' if dark_mode.value else 'Modo claro',
                    icon='dark_mode' if dark_mode.value else 'light_mode',
                ).classes('badge-glass')
                create_theme_toggle(dark_mode)
                ui.button('Iniciar Sesión', icon='login').props('outlined').classes('white-text').on('click', lambda: ui.navigate.to('/login'))
    
    # Contenido principal
    with ui.column().classes('max-w-7xl mx-auto p-8'):
        with ui.row().classes('w-full items-center gap-2 mb-4 opacity-80'):
            ui.icon('tips_and_updates').classes('text-blue-500')
            ui.label('Tu preferencia de tema se guarda automáticamente para próximas visitas.').classes('text-sm')

        # Hero
        with ui.row().classes('w-full items-center gap-8 mb-16 mt-8'):
            with ui.column().classes('flex-1 gap-6'):
                ui.label('Simplifica tus trámites administrativos').classes('text-5xl font-bold leading-tight')
                ui.label(APP_DESCRIPTION).classes('text-xl opacity-70')
                with ui.row().classes('gap-4 mt-4'):
                    ui.button('Comenzar Ahora', icon='rocket_launch', color='blue').classes('text-lg px-8 py-3').on('click', lambda: ui.navigate.to('/login'))
                    ui.button('Ver Demo', icon='play_circle', color='grey').props('outlined').classes('text-lg px-8 py-3').on_click(probar_api)
            
            with ui.card().classes('p-8 gradient-header rounded-3xl'):
                ui.icon('account_balance', size='10rem').classes('white-text')
        
        # Características
        with ui.row().classes('w-full gap-8 mb-16'):
            features = [
                {'icon': 'psychology', 'title': 'IA Avanzada', 'desc': 'Asistente virtual inteligente para tus consultas'},
                {'icon': 'speed', 'title': 'Rápido y Eficiente', 'desc': 'Resuelve trámites en minutos, no en horas'},
                {'icon': 'security', 'title': 'Seguro y Confiable', 'desc': 'Tus datos protegidos con altos estándares'},
            ]
            
            for feature in features:
                with ui.card().classes('flex-1 p-6 text-center'):
                    ui.icon(feature['icon'], size='3rem').classes('text-blue-500 mb-4')
                    ui.label(feature['title']).classes('text-xl font-bold mb-2')
                    ui.label(feature['desc']).classes('opacity-70')
        
        # Estadísticas
        with ui.card().classes('w-full p-8 gradient-header text-white'):
            with ui.row().classes('w-full justify-around text-center'):
                stats = [
                    {'number': '10,000+', 'label': 'Usuarios Activos'},
                    {'number': '50,000+', 'label': 'Trámites Completados'},
                    {'number': '99.9%', 'label': 'Satisfacción'},
                    {'number': '24/7', 'label': 'Disponibilidad'},
                ]
                for stat in stats:
                    with ui.column():
                        ui.label(stat['number']).classes('text-4xl font-bold white-text')
                        ui.label(stat['label']).classes('white-text')
        
        # Footer
        with ui.row().classes('w-full justify-between items-center mt-16 pt-8 border-t'):
            with ui.row().classes('gap-4'):
                ui.label(f'© 2024 {APP_TITLE}').classes('opacity-50')
                ui.label(f'v{APP_VERSION}').classes('opacity-30')
            with ui.row().classes('gap-4'):
                ui.button('Términos', color='grey').props('flat')
                ui.button('Privacidad', color='grey').props('flat')
                ui.button('Contacto', color='grey').props('flat')
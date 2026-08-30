"""Dashboard principal"""

from datetime import datetime
from uuid import uuid4
from nicegui import ui
from utils.constants import APP_TITLE, APP_VERSION, TRAMITES, DEFAULT_AVATAR, AI_AVATAR
from utils.themes import get_theme_css, create_theme_toggle, init_dark_mode

def create_dashboard_page():
    """Crea la página del dashboard"""
    dark_mode = init_dark_mode()
    messages = []
    
    ui.add_head_html(get_theme_css(dark_mode.value))
    
    user = {
        'id': str(uuid4()),
        'name': 'María García López',
        'email': 'maria.garcia@email.es',
        'avatar': DEFAULT_AVATAR,
        'role': 'Ciudadano'
    }
    
    @ui.refreshable
    def chat_messages(own_id: str):
        """Muestra mensajes del chat"""
        if messages:
            for msg_id, msg_name, msg_avatar, text, stamp in messages:
                is_own = own_id == msg_id
                with ui.row().classes(f'w-full {"justify-end" if is_own else "justify-start"} mb-2'):
                    if not is_own:
                        with ui.avatar().classes('w-8 h-8 mr-2 mt-1'):
                            ui.image(msg_avatar)
                    
                    with ui.card().classes(f'max-w-[70%] p-3 rounded-2xl {"message-bubble-own" if is_own else "message-bubble-other"}'):
                        if not is_own:
                            ui.label(msg_name).classes('text-xs font-bold text-blue-600 mb-1')
                        ui.label(text).classes('text-sm leading-relaxed')
                        ui.label(stamp).classes('text-xs opacity-50 mt-1')
                    
                    if is_own:
                        with ui.avatar().classes('w-8 h-8 ml-2 mt-1'):
                            ui.image(msg_avatar)
        else:
            with ui.column().classes('items-center justify-center h-64'):
                ui.icon('psychology', size='4rem').classes('text-blue-200 mb-4')
                ui.label('¡Bienvenido a AC! Soy tu asistente virtual').classes('text-lg font-bold')
                ui.label('¿En qué trámite puedo ayudarte hoy?').classes('text-sm opacity-70')
                with ui.row().classes('gap-2 mt-4 flex-wrap justify-center'):
                    ui.button('IRPF', icon='request_quote', color='blue').props('outline dense').on('click', lambda: send_suggested_message('Necesito ayuda con el IRPF'))
                    ui.button('Renovar DNI', icon='badge', color='blue').props('outline dense').on('click', lambda: send_suggested_message('Quiero renovar el DNI'))
                    ui.button('Licencia', icon='forest', color='blue').props('outline dense').on('click', lambda: send_suggested_message('Información sobre licencia de limpieza de montes'))
        
        ui.run_javascript('''
            setTimeout(() => {
                const container = document.querySelector('.q-scrollarea__container');
                if (container) container.scrollTop = container.scrollHeight;
            }, 50);
        ''')
    
    def send_message():
        """Envía mensaje"""
        if text_input.value.strip():
            stamp = datetime.now().strftime('%H:%M')
            messages.append((user['id'], user['name'], user['avatar'], text_input.value, stamp))
            text_input.value = ''
            chat_messages.refresh()
            ui.timer(0.8, lambda msg=messages[-1][3]: add_ai_response(msg), once=True)

    def send_suggested_message(query: str):
        """Envía una consulta sugerida desde el estado vacío"""
        stamp = datetime.now().strftime('%H:%M')
        messages.append((user['id'], user['name'], user['avatar'], query, stamp))
        chat_messages.refresh()
        ui.timer(0.4, lambda msg=query: add_ai_response(msg), once=True)
    
    def add_ai_response(user_message: str):
        """Respuesta de IA"""
        stamp = datetime.now().strftime('%H:%M')
        responses = {
            'irpf': '📊 Para la declaración del IRPF necesitarás:\n\n• Certificado de retenciones\n• Datos catastrales actualizados\n• Justificantes de deducciones\n\n¿Quieres que te guíe paso a paso?',
            'dni': '🪪 Para renovar el DNI:\n\n1. Pide cita previa en la web oficial\n2. Prepara: foto reciente, DNI anterior\n3. Paga la tasa correspondiente\n\n¿Te ayudo a solicitar la cita?',
            'licencia': '🌲 La licencia de limpieza de montes requiere:\n\n• Solicitud formal (Modelo 023)\n• Plano catastral de la parcela\n• Autorización ambiental\n\n¿Procedemos con la solicitud?',
            'montes': '🌲 La licencia de limpieza de montes requiere:\n\n• Solicitud formal (Modelo 023)\n• Plano catastral de la parcela\n• Autorización ambiental\n\n¿Procedemos con la solicitud?',
        }
        
        response = "🤖 Entiendo tu consulta. Como asistente virtual de la Administración Central, puedo ayudarte con diversos trámites.\n\nPuedo asistirte con:\n• Declaración de IRPF\n• Renovación de DNI\n• Licencias y permisos\n• Certificados oficiales"
        
        for key, resp in responses.items():
            if key in user_message.lower():
                response = resp
                break
        
        messages.append(('ai', 'Asistente AC', AI_AVATAR, response, stamp))
        chat_messages.refresh()
    
    def handle_tramite_click(tramite: dict):
        """Click en trámite"""
        auto_message = f"Quiero información sobre {tramite['name']}"
        stamp = datetime.now().strftime('%H:%M')
        messages.append((user['id'], user['name'], user['avatar'], auto_message, stamp))
        chat_messages.refresh()
        add_ai_response(auto_message)
    
    # Layout principal
    with ui.row().classes('w-full h-screen no-wrap overflow-hidden'):
        # Sidebar
        with ui.column().classes('sidebar w-80 shadow-lg overflow-y-auto'):
            # Perfil
            with ui.column().classes('gradient-header p-6'):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label(APP_TITLE).classes('text-xl font-bold white-text')
                    ui.label(f'v{APP_VERSION}').classes('badge-glass text-xs px-2 py-1 rounded-full')
                
                with ui.row().classes('w-full items-center'):
                    with ui.avatar().classes('w-16 h-16 border-2 border-white'):
                        ui.image(user['avatar'])
                    with ui.column().classes('ml-3'):
                        ui.label(user['name']).classes('font-bold text-lg white-text')
                        ui.label(user['email']).classes('text-xs white-text')
                        with ui.row().classes('mt-1 gap-2'):
                            ui.chip(user['role'], color='white').props('text-color=blue')
                            ui.chip('Verificado', icon='verified', color='green')
                
                with ui.row().classes('w-full mt-4 gap-2'):
                    ui.button('Perfil', icon='person').props('flat dense').classes('profile-btn')
                    ui.button('Ajustes', icon='settings').props('flat dense').classes('profile-btn') 
                    ui.button('Salir', icon='logout').props('flat dense').classes('profile-btn').on('click', lambda: ui.navigate.to('/'))
            
            # Trámites
            with ui.column().classes('p-4'):
                ui.label('TRÁMITES DISPONIBLES').classes('text-xs font-bold opacity-50 mb-3 ml-1')
                
                for tramite in TRAMITES:
                    with ui.row().classes('tramite-card w-full items-center') as card:
                        with ui.element('div').classes('p-2 rounded-xl').style(f'background: {tramite["color"]}20'):
                            ui.icon(tramite['icon']).classes('text-2xl').style(f'color: {tramite["color"]}')
                        with ui.column().classes('ml-3 flex-grow'):
                            ui.label(tramite['name']).classes('text-sm font-semibold')
                            ui.label(tramite['desc']).classes('text-xs opacity-50')
                        ui.icon('chevron_right').classes('opacity-50')
                        card.on('click', lambda t=tramite: handle_tramite_click(t))
                
                ui.separator().classes('my-4')
                
                ui.label('ACCIONES RÁPIDAS').classes('text-xs font-bold opacity-50 mb-3 ml-1')
                actions = [
                    ('Nueva Consulta', 'add_circle'),
                    ('Mis Expedientes', 'folder'),
                    ('Citas Previas', 'event'),
                    ('Notificaciones', 'notifications'),
                ]
                for action, icon in actions:
                    ui.button(action, icon=icon, color='grey').props('flat').classes('w-full text-sm')
            
            # Footer sidebar
            with ui.row().classes('w-full p-4 border-t mt-auto items-center'):
                ui.icon('info').classes('opacity-50 text-sm')
                ui.label('Sesión activa').classes('text-xs opacity-50 ml-2')
                ui.space()
                create_theme_toggle(dark_mode)
        
        # Chat principal
        with ui.column().classes('flex-grow h-screen p-4'):
            # Header chat
            with ui.card().classes('w-full p-4 chat-container mb-4'):
                with ui.row().classes('w-full items-center justify-between'):
                    with ui.row().classes('items-center gap-3'):
                        ui.icon('psychology', size='2rem').classes('text-blue-500')
                        with ui.column():
                            ui.label('Asistente Virtual AC').classes('text-lg font-bold')
                            ui.label('IA generativa para tus trámites').classes('text-xs opacity-70')
                    
                    with ui.row().classes('gap-3 items-center'):
                        with ui.row().classes('items-center gap-1'):
                            ui.element('div').classes('w-2 h-2 rounded-full bg-green-500')
                            ui.label('En línea').classes('text-xs text-green-600')
                        
                        ui.badge('IA Activa', color='purple').classes('text-white')

                        with ui.element('div').classes('chat-header-theme-toggle'):
                            create_theme_toggle(dark_mode)
            
            # Área de chat
            with ui.card().classes('w-full flex-grow chat-container overflow-hidden'):
                with ui.scroll_area().classes('flex-grow'):
                    with ui.column().classes('p-4'):
                        chat_messages(user['id'])
                
                # Input
                with ui.card().classes('w-full p-3 border-t m-0 rounded-none'):
                    with ui.row().classes('w-full items-center gap-2'):
                        ui.button(icon='attach_file', color='grey').props('flat round dense').tooltip('Adjuntar')
                        text_input = ui.input(placeholder='Escribe tu consulta aquí...') \
                            .on('keydown.enter', send_message) \
                            .props('rounded outlined dense').classes('flex-grow message-input')
                        ui.button(icon='send', color='blue').props('flat round dense').on('click', send_message).tooltip('Enviar')
                        ui.button(icon='mic', color='grey').props('flat round dense').tooltip('Dictar')
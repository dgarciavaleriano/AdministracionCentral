"""Componente de chat reutilizable"""

from datetime import datetime
from nicegui import ui
from utils.constants import AI_AVATAR

class ChatComponent:
    """Componente de chat con IA"""
    
    def __init__(self, user_id: str, user_name: str, user_avatar: str):
        self.user_id = user_id
        self.user_name = user_name
        self.user_avatar = user_avatar
        self.messages = []
        self.text_input = None
    
    @ui.refreshable
    def show_messages(self):
        """Muestra los mensajes del chat"""
        if self.messages:
            for msg_id, msg_name, msg_avatar, text, stamp in self.messages:
                is_own = self.user_id == msg_id
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
        
        ui.run_javascript('''
            setTimeout(() => {
                const container = document.querySelector('.q-scrollarea__container');
                if (container) container.scrollTop = container.scrollHeight;
            }, 50);
        ''')
    
    def send_message(self):
        """Envía un mensaje"""
        if self.text_input and self.text_input.value.strip():
            stamp = datetime.now().strftime('%H:%M')
            self.messages.append((self.user_id, self.user_name, self.user_avatar, self.text_input.value, stamp))
            self.text_input.value = ''
            self.show_messages.refresh()
            ui.timer(0.8, lambda msg=self.messages[-1][3]: self.add_ai_response(msg), once=True)
    
    def add_ai_response(self, user_message: str):
        """Añade respuesta de IA"""
        stamp = datetime.now().strftime('%H:%M')
        response = self.simulate_ai_response(user_message)
        self.messages.append(('ai', 'Asistente AC', AI_AVATAR, response, stamp))
        self.show_messages.refresh()
    
    @staticmethod
    def simulate_ai_response(user_message: str) -> str:
        """Simula respuestas de IA"""
        responses = {
            'irpf': '📊 Para la declaración del IRPF necesitarás:\n\n• Certificado de retenciones\n• Datos catastrales actualizados\n• Justificantes de deducciones\n\n¿Quieres que te guíe paso a paso?',
            'dni': '🪪 Para renovar el DNI:\n\n1. Pide cita previa en la web oficial\n2. Prepara: foto reciente, DNI anterior\n3. Paga la tasa correspondiente\n\n¿Te ayudo a solicitar la cita?',
            'licencia': '🌲 La licencia de limpieza de montes requiere:\n\n• Solicitud formal (Modelo 023)\n• Plano catastral de la parcela\n• Autorización ambiental\n\n¿Procedemos con la solicitud?',
            'montes': '🌲 La licencia de limpieza de montes requiere:\n\n• Solicitud formal (Modelo 023)\n• Plano catastral de la parcela\n• Autorización ambiental\n\n¿Procedemos con la solicitud?',
        }
        
        for key, response in responses.items():
            if key in user_message.lower():
                return response
        
        return "🤖 Entiendo tu consulta. Como asistente virtual de la Administración Central, puedo ayudarte con diversos trámites.\n\nPuedo asistirte con:\n• Declaración de IRPF\n• Renovación de DNI\n• Licencias y permisos\n• Certificados oficiales"
    
    def create_input_area(self):
        """Crea el área de input del chat"""
        with ui.row().classes('w-full items-center gap-2'):
            ui.button(icon='attach_file', color='blue').props('flat').on('click', lambda: ui.notify('📎 Función de adjuntar archivos no implementada', type='warning'))
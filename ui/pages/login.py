"""Página de login y registro"""

from nicegui import ui
from utils.constants import APP_TITLE, USER_ROLES
from utils.themes import get_theme_css, create_theme_toggle, init_dark_mode

def create_login_page():
    """Crea la página de login"""
    dark_mode = init_dark_mode()
    ui.add_head_html(get_theme_css(dark_mode.value))
    
    form_state = {'mode': 'login'}
    
    @ui.refreshable
    def login_form():
        """Formulario de inicio de sesión"""
        with ui.column().classes('w-full gap-4'):
            ui.icon('account_circle', size='4rem').classes('text-blue-500 mx-auto')
            ui.label('Iniciar Sesión').classes('text-2xl font-bold text-center')
            ui.label('Accede a tu cuenta de Administración Central').classes('opacity-70 text-center mb-4')
            
            email = ui.input('Email', placeholder='tu@email.com').props('outlined').classes('w-full')
            password = ui.input('Contraseña', password=True, password_toggle_button=True).props('outlined').classes('w-full')
            
            with ui.row().classes('w-full justify-between items-center'):
                ui.checkbox('Recordarme')
                ui.button('¿Olvidaste tu contraseña?', color='blue').props('flat dense').on('click', lambda: change_form('forgot'))
            
            ui.button('Iniciar Sesión', icon='login', color='blue').classes('w-full text-lg py-3').on('click', lambda: do_login(email.value, password.value))
            
            with ui.row().classes('w-full justify-center mt-4'):
                ui.label('¿No tienes cuenta?').classes('opacity-70')
                ui.button('Registrarse', color='green').props('flat dense').on('click', lambda: change_form('register'))
    
    @ui.refreshable
    def register_form():
        """Formulario de registro"""
        with ui.column().classes('w-full gap-4'):
            ui.icon('person_add', size='4rem').classes('text-green-500 mx-auto')
            ui.label('Crear Cuenta').classes('text-2xl font-bold text-center')
            ui.label('Regístrate en Administración Central').classes('opacity-70 text-center mb-4')
            
            name = ui.input('Nombre completo', placeholder='María García').props('outlined').classes('w-full')
            email = ui.input('Email', placeholder='tu@email.com').props('outlined').classes('w-full')
            password = ui.input('Contraseña', password=True, password_toggle_button=True).props('outlined').classes('w-full')
            confirm = ui.input('Confirmar Contraseña', password=True, password_toggle_button=True).props('outlined').classes('w-full')
            
            ui.select(USER_ROLES, value='Ciudadano', label='Tipo de usuario').props('outlined').classes('w-full')
            
            ui.checkbox('Acepto los términos y condiciones')
            
            ui.button('Crear Cuenta', icon='person_add', color='green').classes('w-full text-lg py-3').on('click', lambda: do_register(name.value, email.value, password.value))
            
            with ui.row().classes('w-full justify-center mt-4'):
                ui.label('¿Ya tienes cuenta?').classes('opacity-70')
                ui.button('Iniciar Sesión', color='blue').props('flat dense').on('click', lambda: change_form('login'))
    
    @ui.refreshable
    def forgot_form():
        """Formulario de recuperación"""
        with ui.column().classes('w-full gap-4'):
            ui.icon('lock_reset', size='4rem').classes('text-orange-500 mx-auto')
            ui.label('Recuperar Contraseña').classes('text-2xl font-bold text-center')
            ui.label('Te enviaremos un enlace de recuperación').classes('opacity-70 text-center mb-4')
            
            email = ui.input('Email', placeholder='tu@email.com').props('outlined').classes('w-full')
            
            ui.button('Enviar Enlace', icon='email', color='orange').classes('w-full text-lg py-3').on('click', lambda: do_reset(email.value))
            
            with ui.row().classes('w-full justify-center mt-4'):
                ui.button('Volver al inicio de sesión', icon='arrow_back', color='blue').props('flat').on('click', lambda: change_form('login'))
    
    def change_form(mode: str):
        """Cambia entre formularios"""
        form_state['mode'] = mode
        form_container.clear()
        with form_container:
            if mode == 'login':
                login_form()
            elif mode == 'register':
                register_form()
            else:
                forgot_form()
    
    def do_login(email: str, password: str):
        """Procesa login"""
        if email and password:
            ui.notify('✅ Inicio de sesión exitoso', type='positive', position='top')
            ui.timer(1.0, lambda: ui.navigate.to('/dashboard'), once=True)
        else:
            ui.notify('❌ Completa todos los campos', type='negative', position='top')
    
    def do_register(name: str, email: str, password: str):
        """Procesa registro"""
        if name and email and password:
            ui.notify('✅ Cuenta creada exitosamente', type='positive', position='top')
            ui.timer(1.0, lambda: change_form('login'), once=True)
        else:
            ui.notify('❌ Completa todos los campos', type='negative', position='top')
    
    def do_reset(email: str):
        """Procesa recuperación"""
        if email:
            ui.notify('📧 Enlace de recuperación enviado', type='positive', position='top')
            ui.timer(2.0, lambda: change_form('login'), once=True)
        else:
            ui.notify('❌ Ingresa tu email', type='negative', position='top')
    
    # Header
    with ui.header().classes('gradient-header text-white'):
        with ui.row().classes('w-full max-w-7xl mx-auto items-center justify-between p-4'):
            with ui.row().classes('items-center gap-3'):
                ui.icon('account_balance', size='1.5rem').classes('white-text')
                ui.label(APP_TITLE).classes('text-xl font-bold white-text')
            
            create_theme_toggle(dark_mode)
    
    # Contenedor neutral para evitar estilos de fila de Quasar
    with ui.element('div').classes('login-container'):
        with ui.card().classes('w-full max-w-md p-8 shadow-2xl'):
            form_container = ui.column().classes('w-full')
            with form_container:
                login_form()
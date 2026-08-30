"""Constantes de la aplicación"""

APP_TITLE = "Administración Central (AC)"
APP_VERSION = "2.0.1"
APP_DESCRIPTION = "Tu asistente virtual para trámites administrativos"

# URLs de avatar
DEFAULT_AVATAR = "https://robohash.org/default-user?bgset=bg2&set=set4"
AI_AVATAR = "https://robohash.org/ai-assistant?bgset=bg2&set=set3"

# Datos de trámites
TRAMITES = [
    {"icon": "description", "name": "Declaración IRPF", "desc": "Renta y patrimonio", "color": "#1a73e8"},
    {"icon": "badge", "name": "Renovar DNI", "desc": "Documento Nacional", "color": "#34a853"},
    {"icon": "park", "name": "Limpieza de Montes", "desc": "Licencia forestal", "color": "#ea4335"},
    {"icon": "home", "name": "Certificado Vivienda", "desc": "Habitabilidad", "color": "#fbbc04"},
    {"icon": "directions_car", "name": "Registro Vehículo", "desc": "Matriculación", "color": "#673ab7"},
    {"icon": "medical_services", "name": "Tarjeta Sanitaria", "desc": "Salud pública", "color": "#00bcd4"},
]

# Roles de usuario
USER_ROLES = ["Ciudadano", "Funcionario", "Administrador"]
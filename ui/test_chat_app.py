from nicegui import ui
from nicegui.testing import User


async def test_active_pages_render(user: User) -> None:
    await user.open('/')
    await user.should_see('Simplifica tus trámites administrativos')

    await user.open('/login')
    await user.should_see('Accede a tu cuenta de Administración Central')

    await user.open('/dashboard')
    await user.should_see('Asistente Virtual AC')
    await user.should_see('¿En qué trámite puedo ayudarte hoy?')


async def test_dashboard_returns_a_simulated_response(user: User) -> None:
    await user.open('/dashboard')

    user.find(ui.input).type('Necesito ayuda con el IRPF').trigger('keydown.enter')

    await user.should_see('Necesito ayuda con el IRPF')
    await user.should_see('Para la declaración del IRPF necesitarás:', retries=15)


async def test_landing_validates_api_connection(user: User, monkeypatch) -> None:
    from pages import landing

    monkeypatch.setattr(
        landing.users_api,
        'hello_world',
        lambda: 'Hello from administracioncentral!',
    )

    await user.open('/')
    user.find('Ver Demo').click()

    await user.should_see(
        'API responde: Hello from administracioncentral!',
        retries=15,
    )
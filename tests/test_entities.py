"""Comprueba las decisiones de diseño del modelo, no SQLAlchemy.

Necesitan Postgres:  docker compose up -d --wait db_test
"""

import datetime
import uuid

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from config.settings import settings
from storage.base import Base
from storage.entities import Plan, User

pytestmark = pytest.mark.db

PASSWORD_HASH = "$2b$12$KIXQJ9wZ8vN3pQ7rT2sLxeH0aB1cD4eF5gH6iJ7kL8mN9oP0qR1sT"


def limpiar_esquema(engine) -> None:
    """Borra también `alembic_version`: compartimos base con los tests de migraciones
    y dejarles tablas creadas a mano o un marcador viejo los haría fallar."""
    with engine.begin() as conexion:
        conexion.execute(text("DROP SCHEMA public CASCADE"))
        conexion.execute(text("CREATE SCHEMA public"))


@pytest.fixture(scope="module")
def engine():
    if settings.test_database_url == settings.database_url:
        pytest.fail("TEST_DATABASE_URL apunta a la base de trabajo: estos tests la dropearían.")

    engine = create_engine(
        settings.test_database_url,
        connect_args={"connect_timeout": 5},
        hide_parameters=True,  # igual que el engine real: hay un test que lo comprueba
    )
    limpiar_esquema(engine)
    Base.metadata.create_all(engine)
    yield engine
    limpiar_esquema(engine)
    engine.dispose()


@pytest.fixture
def sesion(engine):
    """Cada test corre en una transacción que se deshace al terminar."""
    conexion = engine.connect()
    transaccion = conexion.begin()
    sesion = Session(bind=conexion, autoflush=False)
    yield sesion
    sesion.close()
    transaccion.rollback()
    conexion.close()


def crear_plan(sesion: Session, nombre: str = "free") -> Plan:
    plan = Plan(
        name=nombre, max_drafts=3, max_sessions_per_day=10, history_retention_days=30
    )
    sesion.add(plan)
    sesion.flush()
    return plan


def crear_usuario(
    sesion: Session,
    plan: Plan,
    email: str = "ana@ejemplo.com",
    nif: str = "12345678Z",
) -> User:
    usuario = User(
        name="Ana",
        surname_1="García",
        nif=nif,
        birthdate=datetime.date(1990, 5, 17),
        email=email,
        password_hash=PASSWORD_HASH,
        phone="600123456",
        fiscal_address="Calle Mayor 1, Madrid",
        plan_id=plan.id,
    )
    sesion.add(usuario)
    sesion.flush()
    return usuario


def test_los_valores_por_defecto_los_pone_el_servidor(sesion: Session):
    plan = crear_plan(sesion)
    usuario = crear_usuario(sesion, plan)

    assert isinstance(plan.id, uuid.UUID)
    assert plan.is_active is True
    assert usuario.status == "active"
    assert usuario.email_verified is False
    assert usuario.preferences == {}


def test_created_at_lleva_zona_horaria(sesion: Session):
    plan = crear_plan(sesion)
    assert plan.created_at.tzinfo is not None, "la columna debe ser TIMESTAMPTZ, no TIMESTAMP"


def test_el_email_duplicado_se_rechaza(sesion: Session):
    plan = crear_plan(sesion)
    crear_usuario(sesion, plan, email="ana@ejemplo.com", nif="11111111H")

    with pytest.raises(IntegrityError) as error:
        crear_usuario(sesion, plan, email="ana@ejemplo.com", nif="22222222J")

    assert "uq_users_email" in str(error.value), "la restricción debe seguir la convención de nombres"


def test_las_excepciones_no_filtran_datos_personales(sesion: Session):
    """Sin hide_parameters el error llevaría el hash, el teléfono y la dirección."""
    plan = crear_plan(sesion)
    crear_usuario(sesion, plan, email="ana@ejemplo.com", nif="11111111H")

    with pytest.raises(IntegrityError) as error:
        crear_usuario(sesion, plan, email="ana@ejemplo.com", nif="22222222J")

    mensaje = str(error.value)
    assert PASSWORD_HASH not in mensaje
    assert "600123456" not in mensaje
    assert "Calle Mayor 1" not in mensaje


def test_no_se_puede_apuntar_a_un_plan_inexistente(sesion: Session):
    plan_fantasma = Plan(
        name="fantasma", max_drafts=1, max_sessions_per_day=1, history_retention_days=1
    )
    plan_fantasma.id = uuid.uuid4()  # nunca se guarda, así que no existe en la base

    with pytest.raises(IntegrityError):
        crear_usuario(sesion, plan_fantasma)


def test_no_se_puede_borrar_un_plan_con_usuarios(sesion: Session):
    """ON DELETE RESTRICT: la supresión es una anonimización controlada, no un DELETE."""
    plan = crear_plan(sesion)
    crear_usuario(sesion, plan)

    sesion.delete(plan)
    with pytest.raises(IntegrityError):
        sesion.flush()


def test_el_jsonb_conserva_una_mutacion_in_place(sesion: Session):
    """Sin MutableDict el cambio se perdería sin dar ningún error."""
    plan = crear_plan(sesion)
    usuario = crear_usuario(sesion, plan)

    usuario.preferences["tema"] = "oscuro"
    sesion.flush()
    sesion.expire(usuario)

    assert usuario.preferences == {"tema": "oscuro"}


def test_se_puede_consultar_dentro_del_jsonb(sesion: Session):
    plan = crear_plan(sesion)
    usuario = crear_usuario(sesion, plan)
    usuario.preferences = {"tema": "oscuro", "idioma": "es"}
    sesion.flush()

    encontrado = sesion.scalars(
        select(User).where(User.preferences["tema"].astext == "oscuro")
    ).one()
    assert encontrado.id == usuario.id


def test_updated_at_no_cambia_dentro_de_la_misma_transaccion(sesion: Session):
    """`now()` devuelve el instante de inicio de la transacción, no el del statement."""
    plan = crear_plan(sesion)
    usuario = crear_usuario(sesion, plan)

    usuario.phone = "699999999"
    sesion.flush()
    sesion.expire(usuario)

    assert usuario.updated_at == usuario.created_at


def test_updated_at_cambia_entre_transacciones(engine):
    with Session(engine) as primera:
        plan = crear_plan(primera, nombre="plan-updated-at")
        usuario = crear_usuario(primera, plan, email="upd@ejemplo.com", nif="99999999R")
        primera.commit()
        usuario_id, plan_id, antes = usuario.id, plan.id, usuario.updated_at

    # get_one y no get: una fila que falte aquí es un fallo del test, no un caso a tratar.
    with Session(engine) as segunda:
        segunda.get_one(User, usuario_id).phone = "699999999"
        segunda.commit()
        despues = segunda.get_one(User, usuario_id).updated_at

    with Session(engine) as limpieza:  # esta prueba sí escribe de verdad
        limpieza.delete(limpieza.get_one(User, usuario_id))
        limpieza.delete(limpieza.get_one(Plan, plan_id))
        limpieza.commit()

    assert despues > antes

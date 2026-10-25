import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from storage.entities import Plan, User


def new_user(email="prueba@test.local", nif="12345678Z"):
    return User(
        name="Ana",
        surname_1="García",
        nif=nif,
        birthdate=datetime.date(1990, 5, 17),
        email=email,
        password_hash="hash-de-prueba",
    )


def test_create_user_with_defaults(db):
    user = new_user()
    db.add(user)
    db.flush()  # manda el INSERT sin hacer commit

    assert user.id is not None
    assert user.status == "active"
    assert user.email_verified is False


def test_duplicate_email_is_rejected(db):
    db.add(new_user(nif="11111111H"))
    db.flush()

    db.add(new_user(nif="22222222J"))
    with pytest.raises(IntegrityError):
        db.flush()


def test_user_with_plan(db):
    plan = Plan(name="plan-de-prueba", max_drafts=3, max_sessions_per_day=10, history_retention_days=30)
    db.add(plan)
    db.flush()

    user = new_user()
    user.plan_id = plan.id
    db.add(user)
    db.flush()

    assert user.plan_id == plan.id

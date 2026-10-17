import pytest

from src import database
from src.create_service import create_employee
from src.update_service import fill_missing_fields


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test.db"

    monkeypatch.setattr(
        database,
        "DB_PATH",
        test_db_path
    )

    database.initialize_database()


def test_missing_required_field(test_database):
    result = create_employee({
        "name": "Deniz"
    })

    assert result["status"] == "needs_input"
    assert "department_id" in result["missing_fields"]


def test_missing_optional_field(test_database):
    result = create_employee({
        "name": "Deniz",
        "department_id": 1,
        "age": 25,
        "salary_try": 50000
    })

    assert result["status"] == "needs_confirmation"
    assert result["null_fields"] == ["email"]


def test_successful_create(test_database):
    result = create_employee(
        {
            "name": "Deniz",
            "department_id": 1
        },
        confirm_nulls=True
    )

    assert result["status"] == "created"

    conn = database.get_connection()
    try:
        row = conn.execute(
            "SELECT name, email FROM employees WHERE id = ?",
            (result["employee_id"],)
        ).fetchone()
    finally:
        conn.close()

    assert row == ("Deniz", None)


def test_invalid_foreign_key(test_database):
    result = create_employee(
        {
            "name": "Deniz",
            "department_id": 9999
        },
        confirm_nulls=True
    )

    assert result["status"] == "error"


def test_update_missing_email(test_database):
    created = create_employee(
        {
            "name": "Deniz",
            "department_id": 1
        },
        confirm_nulls=True
    )

    employee_id = created["employee_id"]

    result = fill_missing_fields(
        employee_id,
        {"email": "deniz@example.com"}
    )

    assert result["status"] == "updated"

    conn = database.get_connection()
    try:
        email = conn.execute(
            "SELECT email FROM employees WHERE id = ?",
            (employee_id,)
        ).fetchone()[0]
    finally:
        conn.close()

    assert email == "deniz@example.com"


def test_cannot_overwrite_existing_email(test_database):
    created = create_employee(
        {
            "name": "Deniz",
            "department_id": 1,
            "email": "deniz@example.com",
            "age": 25,
            "salary_try": 50000
        }
    )

    assert created["status"] == "created"

    result = fill_missing_fields(
        created["employee_id"],
        {"email": "different@example.com"}
    )

    assert result["status"] == "error"
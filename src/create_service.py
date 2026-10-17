import sqlite3
from src.database import get_connection

REQUIRED = ("name", "department_id")
OPTIONAL = ("age", "email", "salary_try")
ALLOWED = set(REQUIRED + OPTIONAL)


def create_employee(data: dict, confirm_nulls=False) -> dict:

    # 1. Bilinmeyen sütun kontrolü
    unknown = set(data) - ALLOWED

    if unknown:
        return {
            "status": "error",
            "message": f"Unknown columns: {sorted(unknown)}"
        }

    # 2. Zorunlu alan kontrolü
    missing = [
        field for field in REQUIRED
        if field not in data or data[field] is None
        or (isinstance(data[field], str) and not data[field].strip())
    ]

    if missing:
        return {
            "status": "needs_input",
            "missing_fields": missing
        }

    # 3. Veri tipi ve iş kuralı kontrolü
    name = data["name"]
    department_id = data["department_id"]
    age = data.get("age")
    email = data.get("email")
    salary = data.get("salary_try")

    if not isinstance(name, str) or not name.strip():
        return {"status": "error", "message": "Invalid name"}

    if type(department_id) is not int:
        return {"status": "error", "message": "Invalid department ID"}

    if age is not None and (
        type(age) is not int or not 0 <= age <= 120
    ):
        return {"status": "error", "message": "Invalid age"}

    if salary is not None and (
        type(salary) is not int or salary < 0
    ):
        return {"status": "error", "message": "Invalid salary"}

    if email is not None and (
        not isinstance(email, str) or not email.strip()
    ):
        return {"status": "error", "message": "Invalid email"}

    # 4. Belirtilmeyen nullable alanları kontrol et
    unspecified = [
        field for field in OPTIONAL if field not in data
    ]

    if unspecified and not confirm_nulls:
        return {
            "status": "needs_confirmation",
            "null_fields": unspecified,
            "message": "Should these fields be saved as NULL?"
        }

    # 5. Veritabanına kayıt ekle
    conn = get_connection()

    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO employees
                (name, age, department_id, email, salary_try)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name.strip(), age, department_id, email, salary)
            )

        return {
            "status": "created",
            "employee_id": cursor.lastrowid
        }

    except sqlite3.IntegrityError as error:
        return {
            "status": "error",
            "message": str(error)
        }

    finally:
        conn.close()
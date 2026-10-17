import sqlite3

from src.database import get_connection

UPDATABLE_FIELDS = {"age", "email", "salary_try"}


def fill_missing_fields(employee_id: int, values: dict) -> dict:
    if not values:
        return {"status": "error", "message": "No values provided."}

    if type(employee_id) is not int or employee_id <= 0:
        return {"status": "error", "message": "Invalid employee ID."}

    if set(values) - UPDATABLE_FIELDS:
        return {"status": "error", "message": "Unsupported fields."}

    for field, value in values.items():
        if field == "age" and (
            type(value) is not int or not 0 <= value <= 120
        ):
            return {"status": "error", "message": "Invalid age."}

        if field == "salary_try" and (
            type(value) is not int or value < 0
        ):
            return {"status": "error", "message": "Invalid salary."}

        if field == "email" and (
            not isinstance(value, str) or not value.strip()
        ):
            return {"status": "error", "message": "Invalid email."}

    conn = get_connection()

    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")

            row = conn.execute(
                "SELECT age, email, salary_try FROM employees WHERE id = ?",
                (employee_id,)
            ).fetchone()

            if row is None:
                return {"status": "error", "message": "Employee not found."}

            current = dict(zip(
                ("age", "email", "salary_try"), row
            ))

            for field in values:
                if current[field] is not None:
                    return {
                        "status": "error",
                        "message": f"{field} already contains a value."
                    }

            assignments = ", ".join(
                f"{field} = ?" for field in values
            )

            conn.execute(
                f"UPDATE employees SET {assignments} WHERE id = ?",
                [*values.values(), employee_id]
            )

        return {"status": "updated", "employee_id": employee_id}

    except sqlite3.IntegrityError as error:
        return {"status": "error", "message": str(error)}

    finally:
        conn.close()
import streamlit as st

from src.database import get_connection
from src.update_service import fill_missing_fields


def render_update_section():
    st.header("Complete Missing Employee Information")

    if "update_feedback" in st.session_state:
        st.success(st.session_state.pop("update_feedback"))

    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT id, name, age, email, salary_try
            FROM employees
            ORDER BY id DESC
        """).fetchall()
    finally:
        conn.close()

    if not rows:
        st.info("No employees found.")
        return

    employees = {
        row[0]: {
            "name": row[1],
            "age": row[2],
            "email": row[3],
            "salary_try": row[4]
        }
        for row in rows
    }

    employee_id = st.selectbox(
        "Select Employee",
        options=list(employees),
        format_func=lambda employee_id: (
            f"{employee_id} - {employees[employee_id]['name']}"
        )
    )

    employee = employees[employee_id]

    missing_fields = [
        field
        for field in ("age", "email", "salary_try")
        if employee[field] is None
    ]

    if not missing_fields:
        st.info("This employee has no missing optional fields.")
        return

    st.write("Missing fields:", ", ".join(missing_fields))

    with st.form("complete_missing_fields"):
        inputs = {
            field: st.text_input(f"Enter {field}")
            for field in missing_fields
        }

        submitted = st.form_submit_button("Update Employee")

    if submitted:
        updates = {}

        try:
            for field, text in inputs.items():
                value = text.strip()

                if not value:
                    continue

                if field in ("age", "salary_try"):
                    updates[field] = int(value)
                else:
                    updates[field] = value

        except ValueError:
            st.error("Age and salary must be whole numbers.")
            return

        if not updates:
            st.warning("Enter at least one value.")
            return

        result = fill_missing_fields(employee_id, updates)

        if result["status"] == "updated":
            st.session_state.update_feedback = (
                f"Employee {employee_id} updated successfully!"
            )
            st.rerun()
        else:
            st.error(result["message"])
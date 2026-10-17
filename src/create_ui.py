import pandas as pd
import streamlit as st

from src.database import get_connection
from src.create_service import create_employee


def render_create_section():

    st.header("Employee Management")

    if "pending_employee" not in st.session_state:
        st.session_state.pending_employee = None

    if "create_feedback" in st.session_state:
        st.success(st.session_state.pop("create_feedback"))

    # Fetch departments from SQLite
    conn = get_connection()

    try:
        departments = conn.execute(
            "SELECT id, name FROM departments ORDER BY name"
        ).fetchall()
    finally:
        conn.close()

    department_options = {
        name: department_id
        for department_id, name in departments
    }

    # STEP 1: CREATE FORM
    if st.session_state.pending_employee is None:

        st.subheader("Add New Employee")

        with st.form("employee_form"):

            name = st.text_input("Employee Name")

            age_text = st.text_input(
                "Age (optional)"
            )

            department = st.selectbox(
                "Department",
                ["-- Select --"] + list(department_options)
            )

            email = st.text_input(
                "Email (optional)"
            )

            salary_text = st.text_input(
                "Salary in TRY (optional)"
            )

            submitted = st.form_submit_button(
                "Review Employee"
            )

        if submitted:

            employee = {}
            valid = True

            if name.strip():
                employee["name"] = name.strip()

            if department != "-- Select --":
                employee["department_id"] = (
                    department_options[department]
                )

            try:
                if age_text.strip():
                    employee["age"] = int(age_text)

                if salary_text.strip():
                    employee["salary_try"] = int(salary_text)

            except ValueError:
                st.error(
                    "Age and salary must be whole numbers."
                )
                valid = False

            if email.strip():
                employee["email"] = email.strip()

            if valid:

                result = create_employee(employee)

                if result["status"] == "needs_input":
                    st.warning(
                        "Missing required fields: "
                        + ", ".join(result["missing_fields"])
                    )

                elif result["status"] == "needs_confirmation":

                    st.session_state.pending_employee = employee
                    st.rerun()

                elif result["status"] == "created":
                    st.session_state.create_feedback = (
                        f"Employee created! ID: "
                        f"{result['employee_id']}"
                    )
                    st.rerun()

                else:
                    st.error(result["message"])

    # STEP 2: CONFIRMATION
    else:

        employee = st.session_state.pending_employee

        st.subheader("Confirm Missing Information")

        missing_fields = [
            field
            for field in ("age", "email", "salary_try")
            if field not in employee
        ]

        st.warning(
            "The following fields were not provided: "
            + ", ".join(missing_fields)
        )

        st.write(
            "These fields will be saved as NULL. "
            "Do you want to continue?"
        )

        st.json(employee)

        if missing_fields:

            with st.expander("Provide Missing Information"):

                with st.form("complete_employee_form"):

                    new_values = {}

                    for field in missing_fields:
                        new_values[field] = st.text_input(
                            f"Enter {field} (optional)"
                        )

                    save_info = st.form_submit_button(
                        "Save Information"
                    )

                if save_info:

                    updates = {}

                    try:
                        for field, value in new_values.items():

                            if not value.strip():
                                continue

                            if field in ("age", "salary_try"):
                                updates[field] = int(value)
                            else:
                                updates[field] = value.strip()

                    except ValueError:
                        st.error(
                            "Age and salary must be integers."
                        )

                    else:
                        if updates:
                            employee.update(updates)

                            st.session_state.pending_employee = (
                                employee
                            )

                            st.rerun()
                        else:
                            st.warning("No information provided.")        


        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Confirm and Create",
                type="primary"
            ):

                result = create_employee(
                    employee,
                    confirm_nulls=True
                )

                if result["status"] == "created":

                    st.session_state.pending_employee = None
                    st.session_state.create_feedback = (
                        f"Employee created! ID: "
                        f"{result['employee_id']}"
                    )
                    st.rerun()

                else:
                    st.error(result)

        with col2:

            if st.button("Cancel"):

                st.session_state.pending_employee = None
                st.rerun()

    # STEP 3: CURRENT EMPLOYEES
    st.subheader("Employees Database")

    conn = get_connection()

    try:
        employees_df = pd.read_sql_query(
            """
            SELECT
                e.id,
                e.name,
                e.age,
                d.name AS department,
                e.email,
                e.salary_try
            FROM employees e
            JOIN departments d
                ON e.department_id = d.id
            ORDER BY e.id DESC
            """,
            conn
        )
    finally:
        conn.close()

    st.dataframe(
        employees_df,
        use_container_width=True
    )
from src.create_service import create_employee

employee = {
    "name": "Deniz",
    "age": 25,
    "department_id": 1,
    "salary_try": 50000
}

result = create_employee(employee)

print("First response:", result)

if result["status"] == "needs_confirmation":

    answer = input(
        "Missing fields will be NULL. Confirm? (y/n): "
    )

    if answer.lower() == "y":
        result = create_employee(
            employee,
            confirm_nulls=True
        )
        print("Final response:", result)
    else:
        print("Operation cancelled.")
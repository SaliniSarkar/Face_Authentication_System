import re


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def validate_registration(name, email, employee_id):
    if not name or not name.strip():
        return "Name is required."

    if not email or not email.strip():
        return "Email is required."

    if not EMAIL_PATTERN.match(email.strip()):
        return "Please enter a valid email address."

    if not employee_id or not employee_id.strip():
        return "Employee ID is required."

    return None

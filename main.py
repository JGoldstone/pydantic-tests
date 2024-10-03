from pydantic_models import Employee

def employee_from_ctor() -> Employee:
    return Employee(name="Chris DeTuma",
                    email="cdetuma@example.com",
                    date_of_birth="1998-04-02",
                    salary=123_000.00,
                    department="IT",
                    elected_benefits=True,)

def employee_from_dict() -> Employee:
    new_employee_dict = {
    "name": "Chris DeTuma",
    "email": "cdetuma@example.com",
    "date_of_birth": "1998-04-02",
    "salary": 123_000.00,
    "department": "IT",
    "elected_benefits": True}
    return Employee.model_validate(new_employee_dict)

def employee_from_json() -> Employee:
    new_employee_json = """
{"employee_id":"d2e7b773-926b-49df-939a-5e98cbb9c9eb",
"name":"Eric Slogrenta",
"email":"eslogrenta@example.com",
"date_of_birth":"1990-01-02",
"salary":125000.0,
"department":"HR",
"elected_benefits":false}
"""
    return Employee.model_validate_json(new_employee_json)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    employee_from_ctor()
    employee_from_dict()
    employee_from_json()

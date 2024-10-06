from typing import Any
from datetime import date, timedelta
from pydantic_models import Employee


def employee_from_ctor() -> Employee:
    return Employee(name="Chris DeTuma",
                    email="cdetuma@example.com",
                    birth_date="1998-04-02",
                    compensation=123_000.00,
                    department="IT",
                    elected_benefits=True, )


def employee_from_dict() -> Employee:
    youngling_birthday: date = date.today() - timedelta(days=365*17)
    new_employee_dict = {
        "name": "Chris DeTuma",
        "email": "cdetuma@example.com",
        "birth_date": youngling_birthday,
        "compensation": 123_000.00,
        "department": "IT",
        "elected_benefits": True}
    return Employee.model_validate(new_employee_dict)


def employee_from_json() -> Employee:
    new_employee_json = """
{"employee_id":"d2e7b773-926b-49df-939a-5e98cbb9c9eb",
"name":"Eric Slogrenta",
"email":"eslogrenta@example.com",
"birth_date":"1990-01-02",
"compensation":125000.0,
"department":"HR",
"elected_benefits":false}
"""
    return Employee.model_validate_json(new_employee_json)


def dump_employee_as_string(employee: Employee) -> dict[str, Any]:
    return employee.model_dump()


def dump_employee_as_json(employee: Employee) -> str:
    return employee.model_dump_json()


def json_schema() -> dict[str, Any]:
    return Employee.model_json_schema()


def it_employee_misspecified() -> None:
    it_employee = {
        "name": "Alexis Tau",
        "email": "ataue@example.com",
        "birth_date": "2001-04-12",
        "compensation": 100_000,
        "department": "IT",
        "elected_benefits": True,
    }
    Employee.model_validate(it_employee)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    employee_from_ctor()
    employee_from_dict()
    e: Employee = employee_from_json()
    e_as_dict: dict[str, Any] = dump_employee_as_string(e)
    e_as_json: str = dump_employee_as_json(e)
    schema: dict[str, Any] = json_schema()
    # print(json.dumps(schema))
    it_employee_misspecified()

foo = Employee(name="foo",
               email='foo@example.com',
               birth_date='1959-11-17',
               compensation=170_000.00,
               department='IT',
               elected_benefits=True)

from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash, verify_password


def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()

def get_employees(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Employee).offset(skip).limit(limit).all()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = models.Employee(employee_name=employee.employee_name, department_id=employee.department_id)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def delete_employee(db:Session, employee_id: int):
    employee = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    if employee is None:
        return None
    db.delete(employee)
    db.commit()
    return employee

def update_employee(db: Session, employee_id : int, employee:schemas.EmployeeUpdate):
    db_employee = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    if db_employee:
        for key, value in employee.dict(exclude_unset=True).items():
            setattr(db_employee, key, value)
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
    return db_employee


def get_department(db: Session, department_id: int):
    return db.query(models.Department).filter(models.Department.department_id == department_id).first()

def get_departments(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Department).offset(skip).limit(limit).all()

def create_department(db: Session, department: schemas.DepartmentCreate):
    db_department = models.Department(department_name = department.department_name)
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

def update_department(db: Session, department_id : int, department:schemas.DepartmentUpdate):
    db_department = db.query(models.Department).filter(models.Department.department_id == department_id).first()
    if db_department:
        for key, value in department.dict(exclude_unset=True).items():
            setattr(db_department, key, value)
        db.add(db_department)
        db.commit()
        db.refresh(db_department)
    return db_department


def delete_department(db:Session, department_id: int):
    department = db.query(models.Department).filter(models.Department.department_id == department_id).first()
    if department is None:
        return None
    db.delete(department)
    db.commit()
    return department

def get_employee_dept(db: Session, skip: int = 0, limit : int = 10):
    employeeEmail = db.query(models.Employee, models.Department).join(models.Department).all()
    results = []

    for employee, department in employeeEmail:
        results.append({
            "employee_id": employee.employee_id,
            "employee_name": employee.employee_name,
            "department_name": department.department_name
        })

    return results


def get_user_by_username(db:Session, username: str):
    return db.query(models.User).filter(models.User.user_name == username).first()

def create_user(db: Session, username: str, password: str, email:str):
    hashed_pw = get_password_hash(password)
    db_user = models.User(user_name=username, password = hashed_pw, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username:str, password: str):
    user = get_user_by_username(db, username)
    if user and verify_password(password, user.password):
        return user
    return None
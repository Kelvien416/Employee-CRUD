from fastapi import FastAPI, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from . import crud, models, schemas, auth
from .database import SessionLocal, engine, get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from typing import Annotated
import app.logconfig as logconfig

#pandaCSV
from fastapi.responses import FileResponse
import pandas as pd
import uuid
from jinja2 import Environment, FileSystemLoader


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
log = logconfig.log_config()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Invalid credentials",
        headers = {"WWW-Authenticate": "Bearer"}
    )  


    try:
        payload = auth.decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise credential_exception
    return user


@app.post("/register")
async def register(user:schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.user_name):
        log.error(f"Failed user registration attempt : {user.user_name} already exist")
        raise HTTPException(status_code=400, detail="Username already registered")
    log.info(f"Created New User : {user.user_name}")
    return crud.create_user(db, user.user_name, user.password, user.email)

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        log.error(f"Failed login attempt")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.user_name})
    log.info(f"Successfull login attempt : {user.user_name}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/logtest")
async def log_test():
    log.info("hello, %s!", "world", key="value!", more_than_strings=[1, 2, 3])
    return {"message": "Log Test"}



@app.get("/me")
async def read_users_me(current_user: schemas.UserCreate = Depends(get_current_user)):
    log.info(f"selected view profile : {current_user.user_name}, by user : {current_user.user_name}")
    return {"username": current_user.user_name}
    

@app.post("/employees/", response_model=schemas.Employee)
async def create_employee(token: Annotated[str, Depends(oauth2_scheme)],employee_name: str = Form(), department_id: int = Form(), db: Session = Depends(get_db),  current_user: schemas.UserCreate = Depends(get_current_user)):
    data = schemas.EmployeeCreate(employee_name=employee_name, department_id=department_id)
    log.info(f"{current_user.user_name} : added employee {employee_name}")
    return crud.create_employee(db=db, employee=data)


@app.get("/employees/{employee_id}", response_model=schemas.Employee)
async def read_employee(employee_id: int, db: Session = Depends(get_db), current_user: schemas.UserCreate = Depends(get_current_user)):
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        log.error(f"{current_user.user_name} : read employee by employee_id")
        raise HTTPException(status_code=404, detail="Employee not found")
    log.info(f"{current_user.user_name} : read employee by employee_id")
    return db_employee

@app.delete("/employees/{employee_id}", response_model=schemas.Employee)
async def delete_employee(
    employee_id: int, 
    db: Session = Depends(get_db), 
    current_user: schemas.UserCreate = Depends(get_current_user)):
    db_employee = crud.delete_employee(db, employee_id=employee_id)
    if db_employee is None:
        log.error(f"{current_user.user_name} : failed to delete employee by employee_id")
        raise HTTPException(status_code=404, detail="Employee not found")
    log.info(f"{current_user.user_name} : deleted employee by employee_id")
    return db_employee

@app.get("/employees/", response_model = list[schemas.Employee])
def read_employees(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: schemas.UserCreate = Depends(get_current_user)):
    employees = crud.get_employees(db, skip=skip, limit=limit)
    log.info(f"{current_user.user_name} : read all employee")
    return employees

@app.get("/employeedept/", response_model = list[schemas.EmployeeDepartment])
def read_emp_dept(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: schemas.UserCreate = Depends(get_current_user)):
    employee_dept = crud.get_employee_dept(db, skip=skip, limit=limit)
    log.info(f"{current_user.user_name} : read all employee dept")
    return employee_dept

@app.get("/employeedept/csvreport", response_model = list[schemas.EmployeeDepartment])
def generate_csv_report(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: schemas.UserCreate = Depends(get_current_user)):
    employee_dept = crud.get_employee_dept(db, skip=skip, limit=limit)
    df = pd.DataFrame(employee_dept)
    file_id = str(uuid.uuid4())
    file_path = f"reports/employee_depatment_report_{file_id}.csv"
    df.to_csv(file_path, index=False)
    log.info(f"{current_user.user_name} : created EmployeeDept report {file_id}")
    
    return FileResponse(
        path = file_path,
        media_type="text/csv",
        filename="employee_report.csv"
    )

@app.get("/employeedept/report2", response_model = list[schemas.EmployeeDepartment])
def read_emp_dept(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: schemas.UserCreate = Depends(get_current_user)):
    employee_dept = crud.get_employee_dept(db, skip=skip, limit=limit)
    env = Environment(loader=FileSystemLoader("app/templates"))
    template = env.get_template("report.html")
    
    html_content = template.render(data=employee_dept)

    with open("reports/employee_report.html", "w") as f:
        f.write(html_content)
    
    log.info(f"{current_user.user_name} : read all employee dept")
    return employee_dept


@app.put("/employees/{employee_id}", response_model=schemas.EmployeeUpdate)
async def update_employee(
    employee_id : int, 
    employee_name: str = Form(), 
    department_id: int = Form(),
    db: Session = Depends(get_db), 
    current_user: schemas.UserCreate = Depends(get_current_user)):
    data = schemas.EmployeeUpdate(
        employee_name=employee_name,
        department_id=department_id
    )
    db_employee = crud.update_employee(db=db, employee_id=employee_id, employee=data )
    if db_employee is None:
        log.error(f"{current_user.user_name} : Failed to update employee_id : {employee_id}")
        raise HTTPException(status_code=404, detail="Employee not found")
    log.info(f"{current_user.user_name} : updated employee_id : {employee_id}")
    return db_employee


@app.post("/departments/", response_model=schemas.Department)
async def create_department(department_name: str = Form(), db: Session = Depends(get_db), current_user: schemas.UserCreate = Depends(get_current_user)):
    data = schemas.DepartmentCreate(department_name= department_name)
    log.info(f"{current_user.user_name} : created department : {department_name}")
    return crud.create_department(db=db, department=data)


@app.get("/departments/{department_id}", response_model=schemas.Department)
async def read_department(department_id: int, db: Session = Depends(get_db), current_user: schemas.UserCreate = Depends(get_current_user)):
    db_department = crud.get_department(db, department_id=department_id)
    if db_department is None:
        log.error(f"{current_user.user_name} : failed to get department by id")
        raise HTTPException(status_code=404, detail="Department not found")
    log.info(f"{current_user.user_name} : get department by id - {department_id}")
    return db_department

@app.get("/departments/", response_model = list[schemas.Department])
async def read_departments(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: schemas.UserCreate = Depends(get_current_user)):
    departments = crud.get_departments(db, skip=skip, limit=limit)
    log.info(f"{current_user.user_name} : get all department data")
    return departments

@app.put("/department/{department_id}", response_model=schemas.Department)
async def update_department(
    department_id : int, 
    department_name : str = Form(), 
    
    db: Session = Depends(get_db), 
    current_user : schemas.UserCreate = Depends(get_current_user)):
    data = schemas.DepartmentUpdate(
        department_name=department_name,
    )
    db_department = crud.update_department(db=db, department_id=department_id, department=data )
    if db_department is None:
        log.error(f"{current_user.user_name} : failed to update department_id : {department_id}")
        raise HTTPException(status_code=404, detail="Department not found")
    log.info(f"{current_user.user_name} : updated department_id : {department_id}")
    return db_department

@app.delete("/department/{department_id}", response_model=schemas.Department)
async def delete_department(
    department_id: int, 
    db: Session = Depends(get_db), 
    current_user: schemas.UserCreate = Depends(get_current_user)):
    db_department = crud.delete_department(db, department_id=department_id)
    
    if db_department is None:
        log.error(f"{current_user.user_name}: failed to delete department id : {department_id}")
        raise HTTPException(status_code=404, detail="Department not found")
    log.info(f"{current_user.user_name} : deleted department_id : {department_id}")
    return db_department

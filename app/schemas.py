from pydantic import BaseModel


class UserBase(BaseModel):
    user_name: str
    email: str
    password: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    user_id: int

    class Config:
        orm_mode = True




class EmployeeBase(BaseModel):
    employee_name: str
    department_id: int

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    employee_id: int

    class Config:
        orm_mode = True





class DepartmetBase(BaseModel):
    department_name: str

class DepartmentCreate(DepartmetBase):
    pass

class DepartmentUpdate(DepartmetBase):
    pass

class Department(DepartmetBase):
    department_id: int

    class Config:
        orm_mode = True


class EmployeeDepartment(BaseModel):
    employee_id : int
    employee_name : str
    department_name: str


class UserCreate(BaseModel):
    user_name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


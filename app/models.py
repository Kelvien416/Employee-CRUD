from sqlalchemy import ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship, declarative_base
from .database import Base


class User(Base):
    __tablename__ = "users_tbl"

    user_id = Column(Integer, primary_key=True, index=True, unique=True)
    user_name = Column(String)
    email = Column(String)
    password = Column(String)
    
class Employee(Base):
    __tablename__ = "employee_tbl"

    employee_id = Column(Integer, primary_key=True, index=True, unique=True)
    employee_name = Column(String)
    department_id = Column(Integer, ForeignKey('department_tbl.department_id'))

    department_tbl = relationship('Department', back_populates='employee_tbl')


class Department(Base):
    __tablename__ = "department_tbl"

    department_id = Column(Integer, primary_key=True, index=True, unique=True)
    department_name = Column(String)

    employee_tbl = relationship('Employee', back_populates='department_tbl')
    
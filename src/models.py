# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from database import engine

Base = declarative_base()

class Countries(Base):
    __tablename__ = 'countries'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Country_Name = Column(String(255), unique=True)

class UserRoles(Base):
    __tablename__ = 'user_roles'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Role_Name = Column(String(255), unique=True)

class Users(Base):
    __tablename__ = 'users'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Username = Column(String(255), unique=True)
    Password = Column(Text)
    Email = Column(String(255), unique=True)
    User_Role = Column(Integer, ForeignKey('user_roles.Id'))

class AirlineCompanies(Base):
    __tablename__ = 'airline_companies'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Airline_Name = Column(String(255), unique=True)
    Country_Id = Column(Integer, ForeignKey('countries.Id'))
    User_Id = Column(Integer, ForeignKey('users.Id'))

class Customers(Base):
    __tablename__ = 'customers'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    First_Name = Column(Text)
    Last_Name = Column(Text)
    Address = Column(Text)
    Phone_No = Column(String(255), unique=True)
    Credit_Card_No = Column(String(255), unique=True)
    User_Id = Column(Integer, ForeignKey('users.Id'), unique=True)

class Administrators(Base):
    __tablename__ = 'administrators'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    First_Name = Column(Text)
    Last_Name = Column(Text)
    User_Id = Column(Integer, ForeignKey('users.Id'))

class Flights(Base):
    __tablename__ = 'flights'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Airline_Company_Id = Column(Integer, ForeignKey('airline_companies.Id'))
    Origin_Country_Id = Column(Integer, ForeignKey('countries.Id'))
    Destination_Country_Id = Column(Integer, ForeignKey('countries.Id'))
    Departure_Time = Column(DateTime)
    Landing_Time = Column(DateTime)
    Remaining_Tickets = Column(Integer)

class Tickets(Base):
    __tablename__ = 'tickets'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Flight_Id = Column(Integer, ForeignKey('flights.Id'), nullable=False)
    Customer_Id = Column(Integer, ForeignKey('customers.Id'), nullable=False)

    __table_args__ = (UniqueConstraint('Flight_Id', 'Customer_Id', name='uq_tickets'),)

# Create tables in the database
Base.metadata.create_all(bind=engine)

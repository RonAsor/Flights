# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from database import engine

Base = declarative_base()

class Countries(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_name = Column(String(255), unique=True)

class UserRoles(Base):
    __tablename__ = 'user_roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(255), unique=True)

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True)
    password = Column(Text)
    email = Column(String(255), unique=True)
    user_role = Column(Integer, ForeignKey('user_roles.id'))

class AirlineCompanies(Base):
    __tablename__ = 'airline_companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    airline_name = Column(String(255), unique=True)
    country_id = Column(Integer, ForeignKey('countries.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

class Customers(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(Text)
    last_name = Column(Text)
    address = Column(Text)
    phone_no = Column(String(255), unique=True)
    credit_card_mo = Column(String(255), unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)

class Administrators(Base):
    __tablename__ = 'administrators'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(Text)
    last_name = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))

class Flights(Base):
    __tablename__ = 'flights'

    id = Column(Integer, primary_key=True, autoincrement=True)
    airline_company_id = Column(Integer, ForeignKey('airline_companies.id'))
    origin_country_id = Column(Integer, ForeignKey('countries.id'))
    destination_country_id = Column(Integer, ForeignKey('countries.id'))
    departure_time = Column(DateTime)
    landing_time = Column(DateTime)
    remaining_tickets = Column(Integer)

class Tickets(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_id = Column(Integer, ForeignKey('flights.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)

    __table_args__ = (UniqueConstraint('flight_id', 'customer_id', name='uq_tickets'),)

# Create tables in the database
Base.metadata.create_all(bind=engine)

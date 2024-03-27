from datetime import date
from models import *
from repository import Repository
from flask import request
from database import Session

class FacadesBase():
        
    def get_all_flights(self):
        session = Session()
        repo = Repository(session=session)
        return repo.get_all(Flights).fetchall()
    
    def get_flights_by_id(self, id: int):
        session = Session()
        repo = Repository(session=session)
        return repo.get_all(Flights).fetchall()

    def get_flights_by_parameters(self, origin_country_id: int, destination_country_id: int, date: date):
        session = Session()
        repo = Repository(session=session)
        return repo.get_flights_by_parameters(origin_country_id,destination_country_id,date).fetchall()
        
    def get_all_airlines(self):
        session = Session()
        repo = Repository(session=session)
        return repo.get_all(AirlineCompanies).fetchall()
    
    def get_airline_by_id(self, id: int):
        session = Session()
        repo = Repository(session=session)
        return repo.get_by_id(AirlineCompanies, id).one()
        
    def get_airline_by_parameters(self, **kwargs):
        session = Session()
        repo = Repository(session=session)
        return repo.get_all(AirlineCompanies, kwargs).one()
    
    def get_all_countries(self):
        session = Session()
        repo = Repository(session=session)
        return repo.get_all(Countries).fetchall()
    
    def get_country_by_id(self, id: int):
        session = Session()
        repo = Repository(session=session)
        return repo.get_by_id(Countries, id).one()
    
    def create_new_user(self, user: Users):
        session = Session()
        repo = Repository(session=session)
        repo.add(user)
        return repo.get_user_by_username(user.username).one()
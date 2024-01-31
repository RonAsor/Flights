from datetime import date
from src.models import *
from src.repository import Repository
from flask import request
from src.database import Session
from src.tokens import Token

class FacadesBase():
    def __init__(self,token:Token):
        self.token = token
        
    def get_all_flights(self):
        session = Session()
        repo = Repository(session=session)
        return repo.get_all(Flights)
    
    def get_flights_by_id(self, id: int):
        session = Session()
        repo = Repository(session=session)
        return repo.get_all(Flights)

    def get_flights_by_parameters(self, origin_country_id: int, destination_country_id: int, date: date):
        session = Session()
        repo = Repository(session=session)
        return repo.get_flights_by_parameters(origin_country_id,destination_country_id,date)
        
    def get_all_airlines(self):
        session = Session()
        repo = Repository(session=session)
        return repo.get_all(AirlineCompanies)
    
    def get_airline_by_id(self, id: int):
        session = Session()
        repo = Repository(session=session)
        return repo.get_by_id(AirlineCompanies, id)
        
    def get_airline_by_parameters(self, **kwargs):
        session = Session()
        repo = Repository(session=session)
        return repo.get_all(AirlineCompanies, kwargs)
    
    def get_all_countries(self):
        session = Session()
        repo = Repository(session=session)
        return repo.get_all(Countries)
    
    def get_country_by_id(self, id: int):
        session = Session()
        repo = Repository(session=session)
        return repo.get_by_id(Countries, id)
    
    def create_new_user(self, user: Users):
        session = Session()
        repo = Repository(session=session)
        repo.add(user)
        
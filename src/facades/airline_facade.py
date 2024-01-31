from src.facades.facades_base import FacadesBase
from src.database import Session
from src.repository import Repository
from src.models import *
from src.tokens import Token

class AirlineFacade(FacadesBase):
    pass
    
    
    def __init__(self,token: Token):
        super().__init__(token)
    
    def get_my_flights(self):
        repo = Repository(session=Session())
        airlines:list[AirlineCompanies] = repo.get_all(AirlineCompanies,{"user_id":self.token.id})
        tickets:list[Tickets] = repo.get_all(Tickets,{"user_id":airlines[0].id})
        if len(airlines) == 1:
            return tickets
        
        repo.log(f'error: found {len(airlines)} instead of 1')
        
    def add_airline(self,airline: AirlineCompanies):
        repo = Repository(session=Session())
        repo.add(airline)
        repo.log(f'Success adding airline {airline}')
    
    
    #check what the update methods do
    def update_airline(self,airline: AirlineCompanies):
        repo = Repository(session=Session())
        airlines:list[AirlineCompanies] = repo.get_all(AirlineCompanies,{"user_id":self.token.id})
        #tickets:list[Tickets] = repo.get_all(Tickets,{"user_id":airlines[0].id})
        if len(airlines) == 1:
            return tickets
        
        repo.log(f'error: found {len(airlines)} instead of 1')
    
    def add_flight(self,flight: Flights):
        repo = Repository(session=Session())
        repo.add(flight)
        repo.session.close()
        
    #check what update does here too        
    def update_flight(self,flight: Flights):
        pass
    
    def remove_flight(self,flight: Flights):
        repo = Repository(session=Session())
        repo.remove(Flights,flight.id)
        repo.session.close()
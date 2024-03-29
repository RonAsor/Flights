from database import Session
from repository import Repository
from models import *
from facades.tokens import LoginToken
from facades.anonymous_facade import FacadesBase
class AirlineFacade(FacadesBase):
    pass
    
    
    def __init__(self,token: LoginToken):
        super().__init__()
        self.role = 'Airline'
        self.token = token
    
    def get_my_flights(self):
        repo = Repository(session=Session())
        airlines:list[AirlineCompanies] = repo.get_all(AirlineCompanies,{"user_id":self.token.id})
        tickets:list[Tickets] = repo.get_all(Tickets,{"customer_id":airlines[0].id})
        if len(airlines) == 1:
            return tickets
        
        repo.log(f'error: found {len(airlines)} instead of 1','error')
        
    def add_airline(self,airline: AirlineCompanies):
        repo = Repository(session=Session())
        repo.add(airline)
        repo.log(f'Success adding airline {airline}','info')
    
    
    #check what the update methods do, should update the existing values with values changed by the user and COMMIT them at the end. currently unsupported
    def update_airline(self,airline: AirlineCompanies):
        repo = Repository(session=Session())
        airlines:list[AirlineCompanies] = repo.get_all(AirlineCompanies,{"user_id":self.token.id})
        #tickets:list[Tickets] = repo.get_all(Tickets,{"user_id":airlines[0].id})
        tickets = ''
        if len(airlines) == 1:
            repo.session.close()
            return tickets
        
        repo.log(f'error: found {len(airlines)} instead of 1')
        repo.session.close()
        
        
    
    #adds a flight to the database, working, should check criterias for the IF statement
    def add_flight(self,flight: Flights):
        repo = Repository(session=Session())
        if flight.remaining_tickets > 0 and flight.landing_time>flight.departure_time: #and flight.origin_country_id != flight.destination_country_id:
            repo.add(flight)
            repo.session.close()
            
        elif flight.remaining_tickets <=0:
            repo.session.close()
            return 'Not enough tickets for selected flight'
        
    #check what update does here too, gets flight information and updates it with session.commit from repo.update        
    def update_flight(self,flight: Flights,**kwargs):
        repo = Repository(session=Session())
        res: Flights = repo.get_by_id(Flights,flight.airline_company_id)
        if self.token.id == res.airline_company_id:
            repo.update(flight)
            repo.session.close()

        
    def remove_flight(self,flight: Flights.id):
        repo = Repository(session=Session())
        repo.remove(Flights,flight)
        repo.session.close()
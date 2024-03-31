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
    
    def get_my_flights(self,id:int):
        repo = Repository(session=Session())
        flights:list[Flights] = repo.get_all(Flights,airline_company_id=id)
        return flights
        #tickets:list[Tickets] = repo.get_all(Tickets,{"customer_id":airlines[0].id})
        #if len(airlines) == 1:
        #    return tickets
        
        repo.log(f'error: found {len(airlines)} instead of 1','error')
        
    
    #check what the update methods do, should update the existing values with values changed by the user and COMMIT them at the end. currently unsupported
    def update_airline(self,airline: AirlineCompanies,user:Users):
        repo = Repository(session=Session())
        repo.update(airline)
        repo.update(user)
        repo.session.close()
        
        
    
    #adds a flight to the database, working, should check criterias for the IF statement
    def add_flight(self,flight: Flights) -> Flights:
        repo = Repository(session=Session())
        if int(flight.remaining_tickets) > 0 and flight.landing_time>flight.departure_time: #and flight.origin_country_id != flight.destination_country_id:
            repo.add(flight)
            flightobj = repo.get_flights_by_parameters(flight.origin_country_id,flight.destination_country_id,flight.departure_time)[-1]
            repo.session.close()
            return flightobj
            
        elif int(flight.remaining_tickets) <=0:
            repo.session.close()
            return 'Cannot add flight with ticket amount less or equal to 0'
        
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
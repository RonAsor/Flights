from database import Session
from repository import Repository
from models import *
from facades.tokens import LoginToken
from facades.anonymous_facade import FacadesBase
class AirlineFacade(FacadesBase):
    '''
    Date: 03/04/24
    Author: Ron Asor
    Description: Class to handle an Airline object user's available actions
    '''
    
    
    def __init__(self,token: LoginToken):
        super().__init__()
        self.role = 'Airline'
        self.token = token
    
    def get_my_flights(self,id:int):
        repo = Repository(session=Session())
        flights:list[Flights] = repo.get_all(Flights,airline_company_id=id)
        return flights
        
    #commit airline and user changes if any provided
    def update_airline(self,airline:AirlineCompanies,user:Users,repo:Repository=None):
        try:
            if not repo:
                repo = Repository(session=Session())
                repo.log(f'Commiting : {airline} with id: {airline.id}, and {user} with {user.id}','info')
                repo.update()
                repo.session.close()
                return True
            if repo:
                repo.log(f'Commiting : {airline.__tablename__} with id: {airline.id}, and {user.__tablename__} with {user.id}','info')
                repo.update()
                repo.session.close()
                return True

        except Exception as e:
            repo.log(f'FAILED Commiting : {airline.__tablename__} with id: {airline.id}, and {user.__tablename__} with {user.id}, with error code {e}','error')
            return False
        
    
    #adds a flight to the database, working, should check conditional criterias for the IF statement
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
        
    #check what update does here too, gets flight information and updates it with session.commit from repo.update. still needs work       
    def update_flight(self,flight: Flights,repo:Repository=None):
        if not repo:
            repo = Repository(session=Session())
            repo.update(flight)
            repo.session.close()
        repo.update(flight)
            
    def remove_flight(self,flight: Flights.id):
        repo = Repository(session=Session())
        repo.remove(Flights,flight)
        repo.session.close()
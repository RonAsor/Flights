from src.database import Session
from src.repository import Repository
from src.models import *
from src.tokens import Token
from src.facades.anonymous_facade import AnonymousFacade

class CustomerFacade(AnonymousFacade):
    
    def __init__(self,token: Token):
        super().__init__(token)
        
    
    def update_customer(self,customer:Customers):
        repo = Repository(session=Session())
        ###
        repo.update(customer)
        self.customer = customer
        repo.session.close()
        
    def add_ticket(ticket:Tickets):
        repo = Repository(session=Session())
        repo.add(ticket)
        repo.session.close()
        
    def remove_ticket(ticket):
        repo = Repository(session=Session())
        repo.remove(ticket)
        repo.session.close()
        
    def get_my_tickets(self):
        repo = Repository(session=Session())
        customers:list[Customers] = repo.get_all(Customers,{"user_id":self.token.id})
        if len(customers) == 1:
            repo.session.close()
            return repo.get_all(Tickets,{"user_id":customers[0].id})
        
        repo.log(f'error: found {len(customers)} Customers instead of 1 on Customerfacade.get_my_tickets')
        repo.session.close()

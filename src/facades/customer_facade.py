from database import Session
from repository import Repository
from models import *
from facades.tokens import LoginToken
from facades.anonymous_facade import FacadesBase

class CustomerFacade(FacadesBase):
    '''
    Date: 03/04/24
    Author: Ron Asor
    Description: Class to handle a Customer object user's available actions
    '''
    
    def __init__(self,token: LoginToken):
        super().__init__()
        self.token = token
        self.role = 'Customer'
        
    def update_customer(self,customer:Customers,user:Users,repo:Repository=None):
        try:
            if not repo:
                repo = Repository(session=Session())
                repo.log(f'Commiting : {customer} with id: {customer.id}, and {user} with {user.id}','info')
                repo.update()
                repo.session.close()
                return True
            if repo:
                repo.log(f'Commiting : {customer.__tablename__} with id: {customer.id}, and {user.__tablename__} with {user.id}','info')
                repo.update()
                repo.session.close()
                return True

        except Exception as e:
            repo.log(f'FAILED Commiting : {customer.__tablename__} with id: {customer.id}, and {user.__tablename__} with {user.id}, with error code {e}','error')
            return False
            
    def add_ticket(ticket:Tickets):
        repo = Repository(session=Session())
        repo.add(ticket)
        repo.session.close()
        
    def remove_ticket(ticket):
        repo = Repository(session=Session())
        repo.remove(ticket)
        repo.session.close()
        
    def get_my_tickets(self) -> Tickets|None:
        repo = Repository(session=Session())
        customer = repo.get_customer_by_username(self.token.name)
        if len(customer) == 1:
            customer_flights = repo.get_all(Tickets,{'customer_id':customer.id})
            repo.session.close()
            return customer_flights
        
        repo.log(f'error: found {len(customer)} Customers instead of 1 on Customerfacade.get_my_tickets',state='error')
        repo.session.close()
        return None
from database import Session
from repository import Repository
from models import *
from facades.tokens import LoginToken
from facades.anonymous_facade import FacadesBase

class CustomerFacade(FacadesBase):
    
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
        
    def get_my_tickets(self):
        repo = Repository(session=Session())
        customers:list[Customers] = repo.get_all(Customers,{"user_id":self.token.id})
        if len(customers) == 1:
            repo.session.close()
            return repo.get_all(Tickets,{"user_id":customers[0].id})
        
        repo.log(f'error: found {len(customers)} Customers instead of 1 on Customerfacade.get_my_tickets')
        repo.session.close()

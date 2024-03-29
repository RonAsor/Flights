from database import Session
from repository import Repository
from models import *
from facades.tokens import LoginToken
from facades.anonymous_facade import FacadesBase

class AdministratorFacade(FacadesBase):
    
    def __init__(self,token: LoginToken):
        super().__init__()
        self.role = 'Administrator'
        self.token = token
        pass
    
    def get_all_customers(self):
        repo = Repository(session=Session())
        customers = repo.get_all(Customers)
        repo.session.close()
        return customers

    def add_airline(self,**kwargs):
        repo = Repository(session=Session())
        repo.add(AirlineCompanies(**kwargs))
        repo.session.close()

    def add_customer(self,**kwargs):
        repo = Repository(session=Session())
        repo.add(Customers(**kwargs))
        repo.session.close()

    def add_administrator(self, **kwargs):
        repo = Repository(session=Session())
        repo.add(Administrators(**kwargs))
        repo.session.close()

    def remove_airline(self,airline:AirlineCompanies):
        repo = Repository(session=Session())
        repo.remove(AirlineCompanies,airline)
        repo.session.close()

    def remove_customer(self,customer:Customers):
        repo = Repository(session=Session())
        repo.remove(Customers,customer)
        repo.session.close()

    def remove_administrator(self,administrator:Administrators):
        repo = Repository(session=Session())
        repo.remove(Administrators,administrator.id)
        repo.session.close()

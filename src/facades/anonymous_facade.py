from src.facades.facades_base import FacadesBase
from src.database import Session
from src.repository import Repository
from src.models import *
from src.tokens import Token
from src.facades.administrator_facade import AdministratorFacade
from src.facades.customer_facade import CustomerFacade
from src.facades.airline_facade import AirlineFacade

class AnonymousFacade(FacadesBase):
    
    def __init__(self,token: Token):
        super().__init__(token)
        
    def login(self,username:Users.username,password:Users.password):
        try:
            repo = Repository(session=Session())
            user:Users = repo.get_user_by_username(username=username).one()
            
            if user.password == password and user.username == username:
                match user.user_role:
                    case 1:
                        return AdministratorFacade(token=self.token)
                    case 2:
                        return AirlineFacade(token=self.token)
                    case 3:
                        return CustomerFacade(token=self.token)

        except Exception as e:
            repo.log(f'error of {e} encountered')
            
from src.facades.facades_base import FacadesBase
from src.database import Session
from src.repository import Repository
from src.models import *
from src.tokens import Token
from src.facades.administrator_facade import AdministratorFacade
from src.facades.customer_facade import CustomerFacade
from src.facades.airline_facade import AirlineFacade
from enum import Enum

class Role(Enum):
    ADMINISTRATORS = 1
    FLIGHTCOMPANY = 2
    CUSTOMER = 3
class AnonymousFacade(FacadesBase):
    
    def __init__(self):
        super().__init__()
        
    def login(self, username: Users.username, password: Users.password):
        try:
            repo = Repository(session=Session())
            user:Users = repo.get_user_by_username(username=username).one()
            
            if user.password == password and user.username == username:
                match user.user_role:
                    case Role.ADMINISTRATORS:
                        return AdministratorFacade(token=Token(id=user.id,name=user.username,role=user.user_role))
                    case Role.FLIGHTCOMPANY:
                        return AirlineFacade(token=Token(id=user.id,name=user.username,role=user.user_role))
                    case Role.CUSTOMER:
                        return CustomerFacade(token=Token(id=user.id,name=user.username,role=user.user_role))
                    case _: 
                        raise ValueError('Unknown user role')
                    
            elif user.password != password:
                return None
            
        except Exception as e:
            repo.log(f'error of {e} encountered')
    
    def add_customer(self,first_name: str, last_name: str, address: str, phone_no: str, credit_card_no: str, user_id: int):
        repo = Repository(session=Session())
        if user_id == self.token.id:
            repo.add(Customers(first_name=first_name, last_name=last_name, address=address, phone_no=phone_no, credit_card_no=credit_card_no, user_id=user_id))
        else:
            raise ValueError('Unauthorized access of user')
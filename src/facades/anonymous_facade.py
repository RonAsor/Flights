from facades.facades_base import FacadesBase
from database import Session
from repository import Repository
from models import *
from facades.tokens import LoginToken
from facades.administrator_facade import AdministratorFacade
from facades.customer_facade import CustomerFacade
from facades.airline_facade import AirlineFacade

class Role():
    ADMINISTRATORS = 1
    FLIGHTCOMPANY = 2
    CUSTOMER = 3
class AnonymousFacade(FacadesBase):
    
    def __init__(self):
        self.user = None
        super().__init__()
        
    def login(self, username: Users.username, password: Users.password)-> AdministratorFacade | AirlineCompanies | CustomerFacade:
        """login function that creates the token of the corresponding Facade, returns self.user which is a initialized object of the correct facade"""
        try:
            repo = Repository(session=Session())
            user:Users = repo.get_user_by_username(username=username).one()
            
            print(user.id,user.username,user.password,user.email,user.user_role,'\n\n')
            if user.password == password and user.username == username:
                match user.user_role:
                    case Role.ADMINISTRATORS:
                        self.user = AdministratorFacade(token=LoginToken(id=user.id,name=user.username,role=user.user_role))
                        return self.user
                    case Role.FLIGHTCOMPANY:
                        self.user = AirlineFacade(token=LoginToken(id=user.id,name=user.username,role=user.user_role))
                        return self.user
                    case Role.CUSTOMER:
                        self.user = CustomerFacade(token=LoginToken(id=user.id,name=user.username,role=user.user_role))
                        return self.user
                    case _: 
                        #default case, in a scenario where role is none of the above, perhaps raise is a bad option here?
                        raise ValueError('Unknown user role')
                    
                    
            elif user.password != password:
                #placeholder in case the password for the user is incorrect, may use the returned value to do certain things (re-render the page/error message etc.)
                self.user = None
                return None
            
        except Exception as e:
            repo.log(f'error encountered '+str(e),state='error')
    
    def add_customer(self,first_name: str, last_name: str, address: str, phone_no: str, credit_card_no: str, user_id: int):
        repo = Repository(session=Session())
        print(user_id,self.user)
        if user_id == self.user.token.id:
            repo.add(Customers(first_name=first_name, last_name=last_name, address=address, phone_no=phone_no, credit_card_no=credit_card_no, user_id=user_id))
        else:
            raise ValueError('Unauthorized access of user')
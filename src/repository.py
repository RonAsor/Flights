from sqlalchemy.orm import Session
from sqlalchemy import text
from src import models
from datetime import datetime
from src.tools.logger import SingletonLogger

class Repository:
    def __init__(self, session: Session):
        self.session = session
        self.logger = SingletonLogger().get_logger()
    
    #region log
    def log(self, message, state):
        match state:
            case "info":self.logger.info(message)
            case "error":self.logger.error(message)
    
    def log_and_execute(self, message, operation, query, params=None, crud_operation=None):
        try:
            self.log(f"{crud_operation} - Executing {operation} - {message}",'info')
            result = self.session.execute(query, params)
            return result
        except Exception as e:
            self.log(f"Error during {operation} - {message}: {str(e)}",'error')
    #endregion    

    #region CRUD
    def get_by_id(self, model, id)-> object:
        try:
            query = self.session.query(model).filter_by(id=id)
            res = query.one_or_none()
            return res
        except Exception as e:
            self.log(f'get_by_id Error:{e}','error')
            return None
    
    def get_all(self, model, **kwargs):
        '''
        Gets all objects of a certain model, if kwargs not provided: return all, else search by those kwargs
        '''
        if kwargs is None:
            query = self.session.query(model)
            results = query.all()
            self.log_and_execute(f"Get all {model.__class__.__name__}", "get_all", query, crud_operation="READ")
            return results
        else:
            query = self.session.query(model).filter_by(**kwargs)
            results = query.all()
            self.log_and_execute(f"Get all {model.__class__.__name__} with params={str(kwargs)}", "get_all", query, crud_operation="READ")
            return results
    
    #need to check if to edit for kwargs
    def add(self, item:models):
        self.item = item
        self.session.add(item)
        self.session.commit()
        self.log(f"Add {item.__class__.__name__} crud_operation='CREATE'",'info')
        
    def update(self,obj) ->bool:
        if obj:
            self.session.commit()
            self.log(f'updated table {obj.__class__.__name__} with id:{obj.id} crud_operation="UPDATE"','info')
            return True
        else:
            return False

    def add_all(self, items):
        try:
            self.session.add_all(items)
            self.session.commit()
            self.log(f"Add all {items} Repository.add_all crud_operation='CREATE'",'info')    
        except Exception as e:
            return self.log(f"Add all error on Repository.add_all: {e}, crud_operation='CREATE'",'error')
        
    def remove(self, model:models,id: int=None):
        try:
            if id:
                query = self.session.query(model).filter_by(id=id).all()
                if query:
                    for obj in query:
                        self.session.delete(obj)
                    self.session.commit()
                    self.log(f"Remove from {query} crud_operation='DELETE'",'info')
        except Exception as e:
            self.log(f"Remove error on Repository.remove: {e}, crud_operation='DELETE'",'error')
    #endregion    
        
    #region db_procedures
    #needs uncluttering : execute_procedure, log_and_execute, log    
    def execute_procedure(self, procedure, params=None):
        query = text(f"EXEC {procedure} {', '.join([f'@_{key}=:_{key}' for key in params.keys()])}")
        return self.log_and_execute(procedure, "execute_procedure", query, params, crud_operation="EXECUTE")

    def get_airline_by_username(self, username:models.Users.username):
        query = "EXEC prc_get_airline_by_username @_username=:username"
        return self.execute_procedure(query, {"username": username})

    def get_customer_by_username(self, username:models.Users.username):
        query = "EXEC prc_get_customer_by_username @_username=:username"
        return self.log_and_execute("Get customer by username", "get_customer_by_username", query, {"username": username})

    def get_flights_by_parameters(self, _origin_country_id:models.Countries.id, _destination_country_id:models.Countries.id, _date:datetime.date):
        query = text(
            "EXEC prc_get_flights_by_parameters @_origin_country_id=:origin_country_id, @_destination_country_id=:destination_country_id, @_date=:date",
            {"origin_country_id": _origin_country_id, "destination_country_id": _destination_country_id, "date": _date}
        )
        return self.log_and_execute("Get flights by parameters", "get_flights_by_parameters", query)

    def get_flights_by_airline_id(self, airline_id:models.AirlineCompanies.id):
        query = "EXEC prc_get_flights_by_airline_id @_airline_id=:airline_id"
        return self.log_and_execute("Get flights by airline ID", "get_flights_by_airline_id", query, {"airline_id": airline_id})

    def get_arrival_flights(self, country_id:models.Countries.id):
        query = "EXEC prc_get_arrival_flights @_country_id=:country_id"
        return self.log_and_execute("Get arrival flights", "get_arrival_flights", query, {"country_id": country_id})

    def get_departure_flights(self, country_id:models.Countries.id):
        query = "EXEC prc_get_departure_flights @_country_id=:country_id"
        return self.log_and_execute("Get departure flights", "get_departure_flights", query, {"country_id": country_id})

    def get_user_by_username(self, username:models.Users.username):
        query = text("EXEC dbo.prc_get_user_by_username @_username=:username")
        return self.log_and_execute("Get user by username", "get_user_by_username", query, {"username": username})

    def get_tickets_by_customer(self, customer_id:models.Users.username):
        query = text("EXEC prc_get_tickets_by_customer @_customer_id=:customer_id")
        return self.log_and_execute("Get tickets by customer", "get_tickets_by_customer", query, {"customer_id": customer_id})

    #region repo-originated db calls
    #needs explicit calling, procedures does not exist

    def get_airlines_by_country(self, country_id: models.Countries.id):
        
        results:list[models.AirlineCompanies] = self.session.query(models.AirlineCompanies).filter(models.AirlineCompanies.country_id == country_id).all()
        self.log(f'get_airlines_by_country: {results}','info')
        return results

    def get_flights_by_origin_country_id(self, country_id: models.Countries.id):
        results:list[models.Flights] = self.session.query(models.Flights).filter(models.Countries.id == country_id)
        self.log(f'get_flights_by_origin_country_id {results}','info')
        return results

    def get_flights_by_destination_country_id(self, country_id: models.Countries.id):
        results:list[models.Flights] = self.session.query(models.Flights).filter(models.Flights.destination_country_id == country_id)
        self.log(f'get_flights_by_destination_country_id {results}','info')
        return results

    def get_flights_by_departure_date(self, date: datetime.date):
        results:list[models.Flights] = self.session.query(models.Flights).filter(models.Flights.departure_time == date)
        self.log('get_flights_by_departure_date','info')
        return results

    def get_flights_by_landing_date(self, date: datetime.date):
        results:list[models.Flights] = self.session.query(models.Flights).filter(models.Flights.landing_time == date)
        self.log(f'get_flights_by_landing_date {results}','info')
        return results

    def get_flights_by_customer(self, customer: models.Customers):
        results:list[models.Flights] = self.session.query(models.Flights).filter(models.Customers.id == customer.id)
        self.log(f'get_flights_by_customer {results}','info')
        return results

    #endregion
    #endregion
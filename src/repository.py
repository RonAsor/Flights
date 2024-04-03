from sqlalchemy.orm import Session
from sqlalchemy import text, Row,CursorResult
import models
from datetime import datetime
from tools.logger import SingletonLogger

class Repository:
    def __init__(self, session: Session):
        self.session = session
        self.logger = SingletonLogger().get_logger()
    
    #region log
    def log(self, message:str, state:str):
        match state:
            case "info":self.logger.info(message)
            case "error":self.logger.error(message)
    
    def log_and_execute(self, message:str, operation:str, query:str, params=None, crud_operation=None) -> CursorResult:
        try:
            self.log(f"Executing {operation} - {message} - CRUD={crud_operation}",state='info')
            result = self.session.execute(text(query), params)
            return result
        except Exception as e:
            self.log(f"Error during {operation} - {message}: {str(e)}",state='error')
    #endregion    

    #region CRUD
    def get_by_id(self, model: models, id: int)-> models.Administrators|models.Customers|models.Users|models.UserRoles|models.AirlineCompanies|models.Flights:
        try:
            query = self.session.query(model).filter_by(id=id)
            res:models = query.one_or_none()
            return res
        except Exception as e:
            self.log(f'get_by_id Error:{e}','error')
            return None
    
    def get_all(self, model: models, **kwargs):
            '''
            Gets all objects of a certain model, if kwargs not provided: return all, else search by those kwargs
            '''
            query = self.session.query(model)
            # Apply filters based on kwargs
            if kwargs:
                query = query.filter_by(**kwargs)
                
            results = query.all()
            
            if results:
                self.log(f"Get all {model.__name__} objects get_all {query.statement} crud_operation=READ",state='info')
            else:
                results = None
                self.log("Get all {model.__name__} objects get_all {query.statement} crud_operation=READ",state='error')
            
            return results
    
    def add(self, item: models):
        self.item = item
        self.session.add(item)
        self.session.commit()
        self.log(f"Add {item.__class__.__name__} crud_operation='CREATE'",'info')
        
    def update(self, model:models=None) -> None:
        print('attempting to commit')
        self.session.commit()
        if model:
            self.log(f'updated table {model.__class__.__name__} with id:{model.id} crud_operation="UPDATE"','info')
            return model

    def add_all(self, items: models):
        try:
            self.session.add_all(items)
            self.session.commit()
            self.log(f"Add all {items} Repository.add_all crud_operation='CREATE'",'info')    
        except Exception as e:
            return self.log(f"Add all error on Repository.add_all: {e}, crud_operation='CREATE'",'error')
        
    def remove(self, model: models, id: int=None):
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
    #needs uncluttering : log_and_execute, log    
    def get_airline_by_username(self, username: str) -> models.AirlineCompanies:
        query = "EXEC prc_get_airline_by_username @_username=:username"
        
        result = self.log_and_execute("Get airline by username", "get_airline_by_username", query, {"username": username},crud_operation='READ')
        try:
            data = result.one()
            return data
        except Exception as e:
            return None

    def get_customer_by_username(self, username: str) -> models.Customers:
        query = "EXEC prc_get_customer_by_username @_username=:username"
        result = self.log_and_execute("Get customer by username", "get_customer_by_username", query, {"username": username},crud_operation='READ')
        data = result.one()

        
        return data

    def get_user_by_username(self, username: str) -> models.Users:
        query = "EXEC dbo.prc_get_user_by_username @_username=:username"
        result = self.log_and_execute("Get user by username", "get_user_by_username", query, {"username": username},crud_operation='READ')
        data = result.one()
        
        return data

    def get_flights_by_parameters(self, origin_country_id: int, destination_country_id: int, date: datetime.date) -> list:
        query = "EXEC prc_get_flights_by_parameters @_origin_country_id=:origin_country_id, @_destination_country_id=:destination_country_id, @_date=:date"
        params = {"origin_country_id": origin_country_id, "destination_country_id": destination_country_id, "date": date}
        data = results = self.log_and_execute("Get flights by parameters", "get_flights_by_parameters", query, params,crud_operation='READ').all()
        return data
    
    def get_flights_by_airline_id(self, airline_id: int) -> list[models.Flights]:
        query = "EXEC prc_get_flights_by_airline_id @_airline_id=:airline_id"
        data = results = self.log_and_execute("Get flights by airline ID", "get_flights_by_airline_id", query, {"airline_id": airline_id},crud_operation='READ').all()
        return data

    def get_arrival_flights(self, country_id: int) -> list[models.Flights]:
        query = "EXEC prc_get_arrival_flights @_country_id=:country_id"
        results = self.log_and_execute("Get arrival flights", "get_arrival_flights", query, {"country_id": country_id},crud_operation='READ').all()
        return results
        
    def get_departure_flights(self, country_id: int) -> list[models.Flights]:
        query = "EXEC prc_get_departure_flights @_country_id=:country_id"
        results = self.log_and_execute("Get departure flights", "get_departure_flights", query, {"country_id": country_id},crud_operation='READ').all()
        return results
    
    def get_tickets_by_customer(self, customer_id: int) -> list[models.Tickets]:
        query = "EXEC prc_get_tickets_by_customer @_customer_id=:customer_id"
        results = self.log_and_execute("Get tickets by customer", "get_tickets_by_customer", query, {"customer_id": customer_id},crud_operation='READ').all()
        return results

    #region repo-originated db calls
    #needs explicit calling, procedures does not exist on the database but handled by the source

    def get_airlines_by_country(self, country_id: models.Countries.id) -> list[models.AirlineCompanies]:
        
        results:list[models.AirlineCompanies] = self.session.query(models.AirlineCompanies).filter(models.AirlineCompanies.country_id == country_id).all()
        self.log(f'get_airlines_by_country: {results}','info')
        return results

    def get_flights_by_origin_country_id(self, country_id: models.Countries.id) -> list[models.Flights]:
        results:list[models.Flights] = self.session.query(models.Flights).filter(models.Countries.id == country_id)
        self.log(f'get_flights_by_origin_country_id {results}','info')
        return results

    def get_flights_by_destination_country_id(self, country_id: models.Countries.id) -> list[models.Flights]:
        results:list[models.Flights] = self.session.query(models.Flights).filter(models.Flights.destination_country_id == country_id)
        self.log(f'get_flights_by_destination_country_id {results}','info')
        return results

    def get_flights_by_departure_date(self, date: datetime.date) -> list[models.Flights]:
        results:list[models.Flights] = self.session.query(models.Flights).filter(models.Flights.departure_time == date)
        self.log('get_flights_by_departure_date','info')
        return results

    def get_flights_by_landing_date(self, date: datetime.date) -> list[models.Flights]:
        results:list[models.Flights] = self.session.query(models.Flights).filter(models.Flights.landing_time == date)
        self.log(f'get_flights_by_landing_date {results}','info')
        return results

    def get_flights_by_customer(self, customer: models.Customers) -> list[models.Flights]:
        results:list[models.Flights] = self.session.query(models.Flights).filter(models.Customers.id == customer.id)
        self.log(f'get_flights_by_customer {results}','info')
        return results

    #endregion
    #endregion
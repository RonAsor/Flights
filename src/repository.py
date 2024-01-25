from sqlalchemy.orm import Session
from sqlalchemy import text
import models
from datetime import datetime
from tools.logger import SingletonLogger

class Repository:
    def __init__(self, session: Session):
        self.session = session
        self.logger = SingletonLogger().get_logger()

    def log_and_execute(self, message, operation, query, params=None, crud_operation=None):
        try:
            self.logger.info(f"{crud_operation} - Executing {operation} - {message}")
            result = self.session.execute(query, params)
            
            # Convert the result to a JSON-compatible format
            return result
        except Exception as e:
            self.logger.error(f"Error during {operation} - {message}: {str(e)}")
            raise

    def execute_procedure(self, procedure, params=None):
        query = text(f"EXEC {procedure} {', '.join([f'@_{key}=:_{key}' for key in params.keys()])}")
        return self.log_and_execute(procedure, "execute_procedure", query, params, crud_operation="EXECUTE")

    def get_by_id(self, model, id):
        query = self.session.query(model).filter_by(id=id)
        return self.log_and_execute(f"Get {model.__name__} by ID", "get_by_id", query, crud_operation="READ")

    def get_all(self, model:models):
        query = self.session.query(model).all()
        return self.log_and_execute(f"Get all {model.__name__}", "get_all", query, crud_operation="READ")
    
    def add(self, item):
        self.session.add(item)
        self.session.commit()
        return self.log_and_execute(f"Add {item}", "Repository.add", item=item, crud_operation="CREATE")

    def update(self, item):
        model_name = item.__class__.__name__
        primary_key = getattr(item, item.__table__.primary_key.columns.keys()[0])

        existing_item = self.session.query(item.__class__).get(primary_key)

        if existing_item:
            for key, value in vars(item).items():
                setattr(existing_item, key, value)

            self.session.commit()
            return self.log_and_execute(f"Update {model_name} with ID {primary_key}", "Repository.update", item=existing_item, crud_operation="UPDATE")
        else:
            self.logger.warning(f"{model_name} with ID {primary_key} not found for update.")
            return None

    def remove(self, item):
        self.session.delete(item)
        self.session.commit()
        return self.log_and_execute(f"Remove {item}", "Repository.remove", item=item, crud_operation="DELETE")

    def add_all(self, items):
        self.session.add_all(items)
        self.session.commit()
        return self.log_and_execute(f"Add all {items}", "Repository.add_all", items=items, crud_operation="CREATE")


    def get_airlines_by_country(self, country_id:models.Countries):
        query = "EXEC prc_get_airlines_by_country @_country_id=:country_id"
        return self.execute_procedure(query, {"country_id": country_id.id})

    def get_flights_by_origin_country_id(self, country_id:models.Countries):
        query = "EXEC prc_get_flights_by_origin_country @_country_id=:country_id"
        return self.execute_procedure(query, {"country_id": country_id.id})

    def get_flights_by_destination_country_id(self, country_id:models.Countries):
        query = "EXEC prc_get_flights_by_destination_country @_country_id=:country_id"
        return self.execute_procedure(query, {"country_id": country_id.id})

    def get_flights_by_departure_date(self, date:datetime.date):
        query = "EXEC prc_get_flights_by_departure_date @_date=:date"
        return self.execute_procedure(query, {"date": date})

    def get_flights_by_landing_date(self, date:datetime.date):
        query = "EXEC prc_get_flights_by_landing_date @_date=:date"
        return self.execute_procedure(query, {"date": date})

    def get_flights_by_customer(self, customer:models.Customers):
        query = "EXEC prc_get_flights_by_customer @_customer_id=:customer_id"
        return self.execute_procedure(query, {"customer_id": customer.id})

    def get_airline_by_username(self, user:models.Users):
        query = "EXEC prc_get_airline_by_username @_username=:username"
        return self.execute_procedure(query, {"username": user.username})

    def get_customer_by_username(self, username:str):
        query = "EXEC prc_get_customer_by_username @_username=:username"
        return self.log_and_execute("Get customer by username", "get_customer_by_username", query, {"username": username}).scalar()

    def get_flights_by_parameters(self, origin_country_id:int, destination_country_id:int, date:datetime.date):
        query = text(
            "EXEC prc_get_flights_by_parameters @_origin_country_id=:origin_country_id, @_destination_country_id=:destination_country_id, @_date=:date",
            {"origin_country_id": origin_country_id, "destination_country_id": destination_country_id, "date": date}
        )
        return self.log_and_execute("Get flights by parameters", "get_flights_by_parameters", query)

    def get_flights_by_airline_id(self, airline_id:int):
        query = "EXEC prc_get_flights_by_airline_id @_airline_id=:airline_id"
        return self.log_and_execute("Get flights by airline ID", "get_flights_by_airline_id", query, {"airline_id": airline_id})

    def get_arrival_flights(self, country_id:int):
        query = "EXEC prc_get_arrival_flights @_country_id=:country_id"
        return self.log_and_execute("Get arrival flights", "get_arrival_flights", query, {"country_id": country_id})

    def get_departure_flights(self, country_id:int):
        query = "EXEC prc_get_departure_flights @_country_id=:country_id"
        return self.log_and_execute("Get departure flights", "get_departure_flights", query, {"country_id": country_id})

    def get_user_by_username(self, username:str):
        query = text("EXEC dbo.prc_get_user_by_username @_username=:username")
        return self.log_and_execute("Get user by username", "get_user_by_username", query, {"username": username})

    def get_tickets_by_customer(self, customer_id:models.Users.username):
        query = text("EXEC prc_get_tickets_by_customer @_customer_id=:customer_id")
        return self.log_and_execute("Get tickets by customer", "get_tickets_by_customer", query, {"customer_id": customer_id})
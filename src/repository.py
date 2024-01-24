from sqlalchemy.orm import Session
from sqlalchemy import text
from flask import jsonify
import models
from datetime import datetime
class Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, model:models, id:int):
        return self.session.query(model).get(id)

    def get_all(self, model:models):
        return self.session.query(model).all()

    def add(self, item):
        self.session.add(item)
        self.session.commit()

    def update(self,item):
        #
        self.session.commit()

    def remove(self, item):
        self.session.delete(item)
        self.session.commit()

    def add_all(self, items):
        self.session.add_all(items)
        self.session.commit()

    def get_airlines_by_country(self, country_id:int):
        self.session.execute()
        # Implement the logic to get airlines by country using the session
        pass

    def get_flights_by_origin_country_id(self, country_id:int):
        # Implement the logic to get flights by origin country id using the session
        pass

    def get_flights_by_destination_country_id(self, country_id:int):
        # Implement the logic to get flights by destination country id using the session
        pass

    def get_flights_by_departure_date(self, date:datetime):
        # Implement the logic to get flights by departure date using the session
        pass

    def get_flights_by_landing_date(self, date:datetime):
        # Implement the logic to get flights by landing date using the session
        pass

    def get_flights_by_customer(self, customer:models.Customers):
        # Implement the logic to get flights by customer using the session
        pass



#region

    def get_airline_by_username(self, username:str):
        result = self.session.execute("EXEC prc_get_airline_by_username @_username=:username", {"username": username})
        return result.scalar()

    def get_customer_by_username(self, username:str):
        result = self.session.execute("EXEC prc_get_customer_by_username @_username=:username", {"username": username})
        return result.scalar()

    def get_flights_by_parameters(self, origin_country_id:int, destination_country_id:int, date:datetime):
        result = self.session.execute(
            "EXEC prc_get_flights_by_parameters @_origin_country_id=:origin_country_id, @_destination_country_id=:destination_country_id, @_date=:date",
            {"origin_country_id": origin_country_id, "destination_country_id": destination_country_id, "date": date}
        )
        return result.fetchall()

    def get_flights_by_airline_id(self, airline_id:int):
        result = self.session.execute("EXEC prc_get_flights_by_airline_id @_airline_id=:airline_id", {"airline_id": airline_id})
        return result.fetchall()

    def get_arrival_flights(self, country_id:int):
        result = self.session.execute("EXEC prc_get_arrival_flights @_country_id=:country_id", {"country_id": country_id})
        return result.fetchall()

    def get_departure_flights(self, country_id:int):
        result = self.session.execute("EXEC prc_get_departure_flights @_country_id=:country_id", {"country_id": country_id})
        return result.fetchall()



    def get_user_by_username(self, username:str):
        query = text("EXEC dbo.prc_get_user_by_username @_username=:username")
        result = self.session.execute(query, {'username': username})
        columns = result.keys()
        # Fetch all rows from the result set, convert & display as json
        rows = result.fetchall()
        data = [dict(zip(columns, row)) for row in rows]
        return jsonify(data)
    
    def get_tickets_by_customer(self, customer_id:str):
        #where we should get the user id and query the server using it
        query = text("EXEC prc_get_tickets_by_customer @_customer_id=:customer_id")
        result = self.session.execute(query, {"customer_id": customer_id})
        rows = result.fetchall()
        columns = result.keys()
        data = [dict(zip(columns,row)) for row in rows]
        return jsonify(data)
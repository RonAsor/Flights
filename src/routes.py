'''
Module used for better organized routing of flask app to endpoints
'''
from flask import render_template,jsonify,request,Flask
from models import Administrators,AirlineCompanies,Countries,Customers,Tickets,UserRoles,Users,Flights
from database import Session
from repository import Repository
from sqlalchemy import CursorResult
from facades.anonymous_facade import AnonymousFacade
from facades.tokens import LoginToken
from facades.administrator_facade import AdministratorFacade
from facades.customer_facade import CustomerFacade
from facades.airline_facade import AirlineFacade

def configure_routes(app:Flask):
    
    @app.route('/users', methods=['GET'])
    def get_all_test():
        session = Session()
        repo = Repository(session)
        users = repo.get_all(Users)
        session.close()
        return render_template('users.html',users=users)
    
    @app.route('/facade_test',methods = ['GET'])
    #test for logging in to a certain facade of certain user, and attempting to create a flight from that user
    def facade_test():
        flightuser:AirlineFacade|AdministratorFacade|CustomerFacade = AnonymousFacade().login('ronasor','hkjfl')
        #add get airline id by user_id
        flight = Flights(
            airline_company_id = 3,
            origin_country_id = 1,
            destination_country_id=1,
            departure_time = "2023-06-05 00:00:00.000",
            landing_time= "2023-08-05 00:00:00.000",
            remaining_tickets=5
            )
        print(flight)
        if isinstance(flightuser,AirlineFacade):
            print('airline facade')
            AirlineFacade.add_flight(flightuser,flight)
        elif isinstance(flightuser,AdministratorFacade):
            AdministratorFacade.add_administrator(flightuser,flight)
            print('admin facade')
            
        elif isinstance(flightuser,CustomerFacade):
            CustomerFacade.add_ticket(flightuser,flight)
            print('customer facade')
            
        return 'ok'
    
    
    #gets roles from the database, test presentation only
    @app.route('/user_roles', methods=['GET'])
    def roles():
        session = Session()
        repo = Repository(session)
        user_roles = repo.get_all(UserRoles)
        session.close()
        return render_template('user_roles.html', user_roles=user_roles)
    
    #shows all airlines
    @app.route('/airlines', methods=['GET'])
    def airlines():
        session = Session()
        repo = Repository(session)
        airlines = repo.get_all(AirlineCompanies)
        session.close()
        return render_template('airlines.html', airlines=airlines)
    
    @app.route('/test', methods=['GET'])
    def placeholder_displays():
        session = Session()
        repo = Repository(session)
        test = repo.get_user_by_username('ronasor')
        data = json_formatter(test)
        session.close()
        return data
    
    @app.route('/test1', methods=['GET'])
    def placeholder_displays2():
        session = Session()
        repo = Repository(session)
        test_result = repo.get_tickets_by_customer(3)
        data = json_formatter(test_result)
        session.close()
        return jsonify(data)
    
    #consider to re-implement as a function and not as page
    @app.route('/create_customer', methods=['POST'])
    def create_customer():
        try:
            # get data from the form
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            address = request.form.get('address')
            phone_no = request.form.get('phone_no')
            credit_card_no = request.form.get('credit_card_no')
            user_id = request.form.get('user_id')
            app.logger.info(f"Received data: {first_name}, {last_name}, {address}, {phone_no}, {credit_card_no}, {user_id}")

            # validation
            if not all([first_name, last_name, address, phone_no, credit_card_no, user_id]):
                app.logger.error("Incomplete data provided")
                return jsonify({"error": "Incomplete data provided"}), 400

            # Logic to create a new customer instance and save it to the database...
            new_customer = Customers(
                first_name=first_name,
                last_name=last_name,
                address=address,
                phone_no=phone_no,
                credit_card_no=credit_card_no,
                user_id=user_id
            )
            session_instance = Session()
            repo = Repository(session=session_instance)
            result = repo.add(new_customer)
            if result:
                return jsonify({"message": "Customer created successfully"}), 201
            else:
                return jsonify({"message":"The entry either already exist or data provided is incorrect"}),418
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            return jsonify({"error": str(e)}), 500
        
    @app.route('/create_admin', methods=['POST'])
    def create_admin():
        try:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            user_id = request.form.get('user_id')
            app.logger.info(f"Received data: {first_name}, {last_name},  {user_id}")

            if not all([first_name, last_name,  user_id]):
                app.logger.error("Incomplete data provided")
                return jsonify({"error": "Incomplete data provided"}), 400

            new_admin = Administrators(
                first_name=first_name,
                last_name=last_name,
                user_id=user_id
            )
            session_instance = Session()
            repo = Repository(session=session_instance)
            repo.add(new_admin)
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            return jsonify({"error": str(e)}), 500
        
    @app.route('/delete_customer', methods=['POST'])
    def delete_customer():
        try:
            id = request.form.get('id')
            if not id:
                app.logger.error("Incomplete data provided")
                return jsonify({"error": "Incomplete data provided"}), 400
            session_instance = Session()
            repo = Repository(session=session_instance)
            customer = repo.get_by_id(Customers,id)
            repo.remove(customer)
            return jsonify({"message": "Customer removed successfully"}), 201
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/get_all' ,methods=['POST'])
    def get_all():
        session = Session()
        repo = Repository(session=session)
        res:list[Administrators]=repo.get_all(Administrators)
        listofadmin = []
        for i in res:
            print(i.first_name)
            listofadmin.append({"name":i.first_name})
        return jsonify(listofadmin),200
    
    @app.route('/prc_call', methods=['POST'])
    def prc_test():
        session = Session()
        repo = Repository(session=session)
        admin: Administrators = repo.get_by_id(Administrators,9)
        admin.first_name = 'eli'
        repo.update(admin)
        return "",200
    
    @app.route('/delete', methods=['POST'])
    def delete():
        #possible placeholder for form delete action
        try:
            id = request.form.get('id')
            tablename = request.form.get('tablename')

            # define the list of table names
            tablenames = ['administrators', 'airline_companies', 'countries', 'customers', 'tickets', 'user_roles', 'users', 'flights']

            # check if the provided tablename is valid
            if tablename.lower() not in tablenames:
                return jsonify({"error": "Invalid tablename"}), 400

            # import the necessary model dynamically based on the tablename
            model = globals()[tablename.capitalize()]
            session = Session()
            repo = Repository(session=session)
            result = repo.remove(model,id)
            if result:
                return jsonify({"message": "Record deleted successfully"}), 200
            else:
                return jsonify(''),204
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def json_formatter(cursor:CursorResult):
            result = cursor.fetchall()
            columns = cursor.keys()
            data = [dict(zip(columns, row)) for row in result] 
            return data
    @app.route('/admin_login', methods=['GET'])
    def login_test():
        id = request.args.get('id')
        new_date=request.args.get('new_date')
        new_date2=request.args.get('new_date2')
        user_name=request.args.get('username')
        password=request.args.get('password')
        anon = AnonymousFacade()
        try:
            facade = anon.login(user_name,password)
            if facade is not None:
                flights = facade.get_flights_by_id(int(id))      
                if len(flights)>0:
                    flight:Flights = flights[0]
                    if new_date:
                        flight.departure_time = new_date
                    if new_date2:
                        flight.landing_time = new_date2
                    facade.update_flight(flight)
        except:
            pass
    if __name__ == '__main__':
        app.run(debug=True)

'''
Module used for better organized routing of flask app to endpoints
'''
from flask import render_template,jsonify,request,Flask,redirect,url_for
from models import Administrators,AirlineCompanies,Countries,Customers,Tickets,UserRoles,Users,Flights
from database import Session
from repository import Repository
from sqlalchemy import CursorResult,Row
from facades.anonymous_facade import AnonymousFacade, Role
from facades.tokens import LoginToken
from facades.administrator_facade import AdministratorFacade
from facades.customer_facade import CustomerFacade
from facades.airline_facade import AirlineFacade

facade = AnonymousFacade()

def configure_routes(app:Flask):
    
    
    #index '/' page reroutes to login
    @app.route('/',methods = ['GET'])
    def index():
        if facade.user:
            return redirect(url_for('dashboard'))
        return redirect(url_for('show_flight_tracker'))
    
     #login, basically the first page we get when we log into the website
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            facade.user = AnonymousFacade.login(facade,username, password)
            if facade.user:
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid credentials')
        return render_template('login.html')

    #dashboard, user controls after logging in
    @app.route('/dashboard')
    def dashboard():
        print(facade.user)
        if not facade.user:
            return redirect(url_for('login'))
        return render_template('dashboard.html', user=facade.user)

    #region  ###Administrator privilege###
    #userlist page, only accessible by administrator endpoint, not visible in dashboard
    @app.route('/users', methods=['GET'])
    def get_all_test():
        if isinstance(facade.user,AdministratorFacade):
            session = Session()
            repo = Repository(session)
            users = repo.get_all(Users)
            session.close()
            return render_template('users.html',users=users)
        return '',404
    
    #admin url for - show_all_administrators, administrators table
    @app.route('/show_all_admins' ,methods=['GET'])
    def show_all_administrators():
        if isinstance(facade.user,AdministratorFacade):
            administratorlist = Repository(session=Session()).get_all(Administrators)
            return render_template('admins.html',administrators=administratorlist,admin_id=facade.user.token.id)
        
        return '',404

    
    #admin route for showing the customer table
    @app.route('/show_all_customers' ,methods=['GET'])
    def show_all_customers():
        if isinstance(facade.user,AdministratorFacade):
            customerlist = facade.user.get_all_customers()
            return render_template('customers.html',customers=customerlist)
        
        return '',404
    
    
    #admin route for showing the customer table
    @app.route('/show_flight_tracker' ,methods=['GET'])
    def show_flight_tracker():
        if isinstance(facade.user,CustomerFacade):
            if facade.user:
                repo = Repository(session=Session())
                user = repo.get_by_id(Users,facade.user.token.id)
                customer = repo.get_user_by_username(username=user.username)
                flight_list = facade.user.get_all_flights()
                repo.session.close()
                return render_template('flight_tracker.html',flights=flight_list,login=facade.user,customer=customer)
        
        elif isinstance(facade.user,AirlineFacade):
            if facade.user:
                #if accessing flight_tracker
                if not request.args.get('action') == 'show_my_flights':
                    repo = Repository(session=Session())
                    #gets user by token, then get the airline
                    user = repo.get_by_id(Users,facade.user.token.id)
                    airline = repo.get_airline_by_username(username=user.username)
                    repo.session.close()
                    if airline is not None:
                        flight_list = facade.user.get_all_flights()
                        return render_template('flight_tracker.html',flights=flight_list,login=facade.user,airline=airline)
                    elif airline is None:
                        return redirect(url_for('index'))
                
                #if accessed through airline dashboard to show my flights
                repo = Repository(session=Session())
                user = repo.get_by_id(Users,facade.user.token.id)
                airline = repo.get_user_by_username(username=user.username)
                my_flight_list = facade.user.get_my_flights(repo.get_airline_by_username(airline.username).id)
                repo.session.close()
                return render_template('flight_tracker.html',flights=my_flight_list,login=facade.user,airline=airline,actions='ALelevated')
            
        elif isinstance(facade.user,AdministratorFacade):
            if facade.user:
                repo = Repository(session=Session())
                user = repo.get_by_id(Users,facade.user.token.id)
                admin = repo.get_user_by_username(username=user.username)
                flight_list = facade.user.get_all_flights()
                repo.session.close()
                return render_template('flight_tracker.html',flights=flight_list,login=facade.user,admin=admin)
            
        elif isinstance(facade,AnonymousFacade):
            flight_list = facade.get_all_flights()
            return render_template('flight_tracker.html',flights=flight_list,login=facade.user)
        
        return render_template('flight_tracker.html',flights=flight_list,login=facade.user)
    
    #admin route for showing the airlines table
    @app.route('/show_all_airlines' ,methods=['GET'])
    def show_all_airlines():
        if isinstance(facade.user,AdministratorFacade):
            airlinelist = facade.user.get_all_airlines()
            return render_template('airlines.html',airlines=airlinelist)
    
        
        return 'invalid'
    
    #route for making a new admin with a form        
    @app.route('/create_administrator', methods=['GET','POST'])
    def create_administrator():
        if isinstance(facade.user,AdministratorFacade):
            if request.method == 'GET':
                try:
                    return render_template('create_administrator.html')
                except Exception as e:
                    pass
            if request.method == 'POST':
                try:
                    # get data from the form
                    first_name = request.form.get('first_name')
                    last_name = request.form.get('last_name')
                    username = request.form.get('username')
                    password = request.form.get('password')
                    email = request.form.get('email')
                    new_user = Users(
                        username = username,
                        password = password,
                        email = email,
                        #all users created as customers, unless admin updates otherwise
                        user_role = Role.ADMINISTRATORS
                        
                    )  
                    
                    # validation
                    if not all([first_name, last_name,username,password,email]):
                        app.logger.error("Data provided incomplete, please refill the form")
                        return render_template('create_administrator.html', error='Data provided incomplete, please refill the form',action='create')
                    facade.create_new_user(new_user)
                    repo = Repository(session=Session())
                    #internally fetching the administrator from database to create an administrator out of it's id & data
                    new_admin_id = repo.get_all(Users)[-1].id

                    # Logic to create a new administrator instance and save it to the database...
                    new_admin = Administrators(
                        first_name=first_name,
                        last_name=last_name,
                        user_id = new_admin_id
                    )
                    facade.user.add_administrator(new_admin)
                    return render_template('create_administrator.html',error='user created!',action='create')

                except Exception as e:
                    app.logger.error(f"An error occurred: {str(e)}")
                    return render_template('create_administrator.html', error='Internal server error',action='create')
        return 'no',404
        
        #route for making a new customer with a form        

    #route for making a new airline with a form        
    @app.route('/create_airline', methods=['GET','POST','PUT'])
    def create_airline():
        if request.method == 'GET':
            try:
                if isinstance(facade.user,AdministratorFacade):
                    if not request.args.get('action') == 'update':
                        return render_template('create_airline.html', action='create')
                
                else:
                    
                    return render_template('create_airline.html',action='update')
                
            except Exception as e:
                pass
            
        #POST for updating a company and creating a new one based on facade
        if request.method == 'POST':
            #updating, airline permissions
            if isinstance(facade.user, AirlineFacade):
                airline_name = request.form.get('airline_name')
                country_id = request.form.get('country_id')
                username = request.form.get('username')
                password = request.form.get('password')
                email = request.form.get('email')
                
                try:
                    # Begin a transaction
                    session = Session()
                    repo = Repository(session=session)
                    
                    # Fetch user object
                    user = repo.get_by_id(Users, facade.user.token.id)
                    
                    # Fetch airline object
                    airlineuser = repo.get_airline_by_username(user.username)
                    #returns obj with all table columns of both user and airline, id belong to airline in this case
                    airline = repo.get_by_id(AirlineCompanies, airlineuser.id)
                    #returns the company object from the airline id
                    
                    # Update airline attributes
                    airline.airline_name = airline_name
                    airline.country_id = country_id
                    
                    # Update user attributes
                    user.username = username
                    user.password = password
                    user.email = email
                    user.user_role = 2
                    
                    # Commit changes to both objects within the same transaction
                    facade.user.update_airline(airline,user,repo=repo)
                    
                    # Close the session
                    session.close()
                    
                    return redirect(url_for('dashboard'))
                except Exception as e:
                    # Roll back the transaction in case of error
                    session.rollback()
                    raise e
                
                
                return redirect(url_for('dashboard'))
            #creating, administrator permissions
            if isinstance(facade.user,AdministratorFacade):
                try:
                    # get data from the form
                    airline_name = request.form.get('airline_name')
                    country_id = request.form.get('country_id')
                    username = request.form.get('username')
                    password = request.form.get('password')
                    email = request.form.get('email')
                    new_user = Users(
                        username = username,
                        password = password,
                        email = email,
                        #all users created as customers, unless admin updates otherwise
                        user_role = Role.FLIGHTCOMPANY
                        
                    )  
                    # validation
                    if not all([airline_name, country_id,username,password,email]):
                        app.logger.error("Data provided incomplete, please refill the form")
                        return render_template('create_airline.html', error='Data provided incomplete, please refill the form',action='create')
                    repo = Repository(session=Session())
                    userobj = repo.get_by_id(Users,new_user)
                    if  userobj is None:
                        facade.create_new_user(new_user)
                        #internally fetching the customer from database to create a customer out of it's id & data
                        new_airline_id = repo.get_all(Users)[-1].id

                        # Logic to create a new customer instance and save it to the database...
                        new_airline = AirlineCompanies(
                            airline_name=airline_name,
                            country_id=country_id,
                            user_id = new_airline_id
                        )
                        facade.user.add_airline(new_airline)

                        return render_template('create_airline.html',error='user created!',action='create')
                    else:
                        return render_template('create_airline.html',error='internal server error',action='create')
                except Exception as e:
                    app.logger.error(f"An error occurred: {str(e)}")
                    return render_template('create_airline.html', error='Internal server error',action='create')
            else:
                return '',404
    
    #route for making a new flight with a form        
    @app.route('/create_flight', methods=['GET','POST'])
    def create_flight():
        if request.method == 'GET':
            try:
                if isinstance(facade.user,AirlineFacade):
                    return render_template('create_flight.html', action='create')
                else:
                    return '',404
            except Exception as e:
                pass
        if request.method == 'POST':
            try:
                if isinstance(facade.user,AirlineFacade):
                    # get data from the form
                    repo = Repository(session=Session())
                    airlineobj = repo.get_airline_by_username(repo.get_by_id(Users,facade.user.token.id).username)
                    
                    
                    origin_country_id = request.form.get('origin_country_id')
                    destination_country_id = request.form.get('destination_country_id')
                    departure_time = request.form.get('departure_time')
                    landing_time = request.form.get('landing_time')
                    remaining_tickets = request.form.get('remaining_tickets')
                    airline_company_id=airlineobj.id
                    
                    new_flight = Flights(
                        airline_company_id=airline_company_id,
                        origin_country_id=origin_country_id,
                        destination_country_id=destination_country_id,
                        departure_time = departure_time,
                        landing_time = landing_time,
                        remaining_tickets = remaining_tickets,
                    )  
                    
                    # validation
                    if not all([origin_country_id, destination_country_id,departure_time,landing_time,remaining_tickets,airlineobj.id]):
                        app.logger.error("Data provided incomplete, please refill the form")
                        return render_template('create_flight.html', error='Data provided incomplete, please refill the form',action='create')
                    dbflight = facade.user.add_flight(flight=new_flight).id
                    #implemented return object, so we can pick the created id from the db, not sure if this is necessary during creation though, not done on the other class objects.
                    
                    #internally fetching the customer from database to create a customer out of it's id & data
                    return render_template('create_flight.html',error='flight created!',action='create')

            except Exception as e:
                app.logger.error(f"An error occurred: {str(e)}")
                return render_template('create_flight.html', error='Internal server error',action='create')
        
    #route for deleting customer from the table, database
    @app.route('/customers/<int:customer_id>', methods=['DELETE'])
    def delete_customer(customer_id):
        if isinstance(facade.user,AdministratorFacade):
            try:
                Repository(session=Session()).remove(Customers,customer_id)
                return 'Customer deleted', 200
            except:
                return 'Customer not found', 404
    
    #route for deleting an admin from the table, database
    @app.route('/admins/<int:admin_id>', methods=['DELETE'])
    def delete_admin(admin_id):
        if isinstance(facade.user,AdministratorFacade):
            try:
                Repository(session=Session()).remove(Administrators,admin_id)
                return 'Admin deleted', 200
            except:
                return 'Admin not found', 404

    #route for deleting an airline from the table, database
    @app.route('/airlines/<int:airline_id>', methods=['DELETE'])
    def delete_airline(airline_id):
        if isinstance(facade.user,AdministratorFacade):
            try:
                Repository(session=Session()).remove(AirlineCompanies,airline_id)
                return 'Airline deleted', 200
            except:
                return 'Airline not found', 404

    #route for deleting a flight from the table, database
    @app.route('/flights/<int:flight_id>', methods=['DELETE'])
    def delete_flight(flight_id):
        if isinstance(facade.user,(AdministratorFacade,AirlineFacade)):
            try:
                Repository(session=Session()).remove(Flights,flight_id)
                return 'Airline deleted', 200
            except:
                return 'Airline not found', 404



    ### End of Administrator privileges ###
    #endregion

    #route for making a new customer with a form        
    @app.route('/create_customer', methods=['GET','POST'])
    def create_customer():
        if request.method == 'GET':
            try:
                return render_template('create_customer.html', action='create')
            except Exception as e:
                pass
        if request.method == 'POST':
            try:
                # get data from the form
                first_name = request.form.get('first_name')
                last_name = request.form.get('last_name')
                address = request.form.get('address')
                phone_no = request.form.get('phone_no')
                credit_card_no = request.form.get('credit_card_no')
                username = request.form.get('username')
                password = request.form.get('password')
                email = request.form.get('email')
                new_user = Users(
                    username = username,
                    password = password,
                    email = email,
                    #all users created as customers, unless admin updates otherwise
                    user_role = Role.CUSTOMER
                    
                )  
                
                # validation
                if not all([first_name, last_name, address, phone_no, credit_card_no,username,password,email]):
                    app.logger.error("Data provided incomplete, please refill the form")
                    return render_template('create_customer.html', error='Data provided incomplete, please refill the form',action='crearte')
                
                
                facade.create_new_user(new_user)
                repo = Repository(session=Session())
                #internally fetching the customer from database to create a customer out of it's id & data
                new_customer_id = repo.get_all(Users)[-1].id

                # Logic to create a new customer instance and save it to the database...
                new_customer = Customers(
                    first_name=first_name,
                    last_name=last_name,
                    address=address,
                    phone_no=phone_no,
                    credit_card_no=credit_card_no,
                    user_id = new_customer_id
                )
                facade.add_customer(new_customer)
                return render_template('create_customer.html',error='user created!',action='create')

            except Exception as e:
                app.logger.error(f"An error occurred: {str(e)}")
                return render_template('create_customer.html', error='Internal server error')
    
    #WIP, still needs object oriented magic
    @app.route('/update_customer', methods=['GET','PUT'])
    def update_customer():
        if (request.method == 'GET'):
            return render_template('/create_customer.html',action='update')
        elif (request.method == 'PUT'):
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            address = request.form.get('address')
            phone_no = request.form.get('phone_no')
            credit_card_no = request.form.get('credit_card_no')
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            updated_user_data = Users(
                username = username,
                password = password,
                email = email,
                #all users created as customers, unless admin updates otherwise
                user_role = Role.CUSTOMER
                    
                )
            newobj = Repository(session=Session()).get_user_by_username(username=username).all()
            updated_customer_data = Customers(
                    first_name=first_name,
                    last_name=last_name,
                    address=address,
                    phone_no=phone_no,
                    credit_card_no=credit_card_no,
                    user_id = facade.user.token.id
                )
    
    #gets roles from the database, test presentation only
    @app.route('/user_roles', methods=['GET'])
    def roles():
        session = Session()
        repo = Repository(session)
        user_roles = repo.get_all(UserRoles)
        session.close()
        return render_template('user_roles.html', user_roles=user_roles)

    #test
    @app.route('/prc_call', methods=['POST'])
    def prc_test():
        session = Session()
        repo = Repository(session=session)
        admin: Administrators = repo.get_by_id(Administrators,9)
        admin.first_name = 'eli'
        repo.update(admin)
        return "",200



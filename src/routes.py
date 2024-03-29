'''
Module used for better organized routing of flask app to endpoints
'''
from flask import render_template,jsonify,request,Flask,redirect,url_for
from models import Administrators,AirlineCompanies,Countries,Customers,Tickets,UserRoles,Users,Flights
from database import Session
from repository import Repository
from sqlalchemy import CursorResult
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
        return redirect(url_for('login'))
    
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
        return 'invalid'
    
    #admin url for - show_all_administrators, administrators table
    @app.route('/show_all_admins' ,methods=['GET'])
    def show_all_administrators():
        if isinstance(facade.user,AdministratorFacade):
            administratorlist = Repository(session=Session()).get_all(Administrators)
            return render_template('admins.html',administrators=administratorlist,admin_id=facade.user.token.id)
        
        return 'invalid'

    
    #admin route for showing the customer table
    @app.route('/show_all_customers' ,methods=['GET'])
    def show_all_customers():
        if isinstance(facade.user,AdministratorFacade):
            customerlist = facade.user.get_all_customers()
            return render_template('customers.html',customers=customerlist)
        
        return 'invalid'
    
    #admin route for showing the customer table
    @app.route('/show_all_airlines' ,methods=['GET'])
    def show_all_airlines():
        if isinstance(facade.user,AdministratorFacade):
            airlinelist = facade.user.get_all_airlines()
            return render_template('airlines.html',airlines=airlinelist)
    
        
        return 'invalid'
    
    #route for making a new admin with a form        
    @app.route('/create_administrator', methods=['GET','POST'])
    def create_administrator():
        if request.method == 'GET':
            try:
                return render_template('create_administrator.html')
            except Exception as e:
                pass
        if request.method == 'POST':
            try:
                print(request.form)
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
                print('newobj:',new_admin_id,'\n')

                # Logic to create a new administrator instance and save it to the database...
                new_admin = Administrators(
                    first_name=first_name,
                    last_name=last_name,
                    user_id = new_admin_id
                )
                repo.add(new_admin)
                repo.session.close()
                return render_template('create_administrator.html',error='user created!',action='create')

            except Exception as e:
                app.logger.error(f"An error occurred: {str(e)}")
                return render_template('create_administrator.html', error='Internal server error',action='create')
        
        #route for making a new customer with a form        

    #route for making a new airline with a form        
    @app.route('/create_airline', methods=['GET','POST'])
    def create_airline():
        if request.method == 'GET':
            try:
                return render_template('create_airline.html', action='create')
            except Exception as e:
                pass
        if request.method == 'POST':
            try:
                print(request.form)
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
                print(airline_name,country_id,username,password,email)
                if not all([airline_name, country_id,username,password,email]):
                    app.logger.error("Data provided incomplete, please refill the form")
                    return render_template('create_airline.html', error='Data provided incomplete, please refill the form',action='create')
                
                facade.create_new_user(new_user)
                repo = Repository(session=Session())
                #internally fetching the customer from database to create a customer out of it's id & data
                new_airline_id = repo.get_all(Users)[-1].id
                print('new_airline_id:',new_airline_id,'\n')


                

                # Logic to create a new customer instance and save it to the database...
                new_airline = AirlineCompanies(
                    airline_name=airline_name,
                    country_id=country_id,
                    user_id = new_airline_id
                )
                repo.add(new_airline)
                repo.session.close()
                return render_template('create_airline.html',error='user created!',action='create')

            except Exception as e:
                app.logger.error(f"An error occurred: {str(e)}")
                return render_template('create_airline.html', error='Internal server error',action='create')
        
    #route for deleting customer from the table, database
    @app.route('/customers/<int:customer_id>', methods=['DELETE'])
    def delete_customer(customer_id):
        if isinstance(facade.user,AdministratorFacade):
            print(customer_id)
            try:
                Repository(session=Session()).remove(Customers,customer_id)
                return 'Customer deleted', 200
            except:
                return 'Customer not found', 404
    
    #route for deleting an admin from the table, database
    @app.route('/admins/<int:admin_id>', methods=['DELETE'])
    def delete_admin(admin_id):
        if isinstance(facade.user,AdministratorFacade):
            print(admin_id)
            try:
                Repository(session=Session()).remove(Administrators,admin_id)
                return 'Admin deleted', 200
            except:
                return 'Admin not found', 404

    #route for deleting an airline from the table, database
    @app.route('/airlines/<int:airline_id>', methods=['DELETE'])
    def delete_airline(airline_id):
        if isinstance(facade.user,AdministratorFacade):
            print(airline_id)
            try:
                Repository(session=Session()).remove(AirlineCompanies,airline_id)
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
                print(request.form)
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
                print('new_customer_id:',new_customer_id,'\n')

                # Logic to create a new customer instance and save it to the database...
                new_customer = Customers(
                    first_name=first_name,
                    last_name=last_name,
                    address=address,
                    phone_no=phone_no,
                    credit_card_no=credit_card_no,
                    user_id = new_customer_id
                )
                repo.add(new_customer)
                repo.session.close()
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
    
        
    # @app.route('/customers', methods=['delete'])
    # def delete_customer(data):
    #     if isinstance(facade.user,AdministratorFacade):
    #         print(data)
    #         facade.user.remove_customer(data)
    

    
    
    #test for logging in to a certain facade of certain user, and attempting to create a flight from that user
    @app.route('/facade_test',methods = ['GET'])
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
    
    #shows all airlines, test
    @app.route('/airlines', methods=['GET'])
    def airlines():
        session = Session()
        repo = Repository(session)
        airlines = repo.get_all(AirlineCompanies)
        session.close()
        return render_template('index.html', airlines=airlines, allairlines=True)
    
    
    #test
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
    
    
    #test
    @app.route('/prc_call', methods=['POST'])
    def prc_test():
        session = Session()
        repo = Repository(session=session)
        admin: Administrators = repo.get_by_id(Administrators,9)
        admin.first_name = 'eli'
        repo.update(admin)
        return "",200
    



    if __name__ == '__main__':
        app.run(debug=True)

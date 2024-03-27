'''
Module used for better organized routing of flask app to endpoints
'''
from flask import render_template,jsonify,request,Flask,redirect,url_for
from models import Administrators,AirlineCompanies,Countries,Customers,Tickets,UserRoles,Users,Flights
from database import Session
from repository import Repository
from sqlalchemy import CursorResult
from facades.anonymous_facade import AnonymousFacade, UserRoles
from facades.tokens import LoginToken
from facades.administrator_facade import AdministratorFacade
from facades.customer_facade import CustomerFacade
from facades.airline_facade import AirlineFacade

facade = AnonymousFacade()

def configure_routes(app:Flask):
    
    @app.route('/users', methods=['GET'])
    def get_all_test():
        session = Session()
        repo = Repository(session)
        users = repo.get_all(Users)
        session.close()
        return render_template('users.html',users=users)
    
    @app.route('/show_all_customers' ,methods=['GET'])
    def show_all_customers():
        if isinstance(facade.user,AdministratorFacade):
            customerlist = facade.user.get_all_customers()
            for customer in customerlist:
                print(customer)    
            return render_template('customers.html',customers=customerlist)
        
        return 'invalid'

    
    @app.route('/',methods = ['GET'])
    def index():
        
        return render_template('index.html')
    
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

    @app.route('/dashboard')
    def dashboard():
        print(facade.user)
        if not facade.user:
            return redirect(url_for('login'))
        return render_template('dashboard.html', user=facade.user)

   
    
    @app.route('/create_customer', methods=['GET','POST'])
    def create_customer():
        if request.method == 'GET':
            try:
                return render_template('create_customer.html')
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
                    user_role = 3
                    
                )   
                facade.create_new_user(new_user)
                repo = Repository(session=Session())
                #internally fetching the customer from database to create a customer out of it's id & data
                newobj = repo.get_user_by_username(new_user.username)
                print('newobj:',newobj,'\n')


                # validation
                if not all([first_name, last_name, address, phone_no, credit_card_no]):
                    app.logger.error("Data provided incomplete, please refill the form")
                    return render_template('create_customer.html', error='Data provided incomplete, please refill the form')

                # Logic to create a new customer instance and save it to the database...
                new_customer = Customers(
                    first_name=first_name,
                    last_name=last_name,
                    address=address,
                    phone_no=phone_no,
                    credit_card_no=credit_card_no,
                    user_id = newobj[0][0]
                )
                repo.add(new_customer)
                repo.session.close()
                return render_template('create_customer.html',error='user created!')

            except Exception as e:
                app.logger.error(f"An error occurred: {str(e)}")
                return render_template('create_customer.html', error='Internal server error')
                # return jsonify({"error": str(e)}), 500
        
    
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

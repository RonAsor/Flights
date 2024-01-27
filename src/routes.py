'''
Module used for better organized routing of flask app to endpoints
'''
from flask import render_template,jsonify,request,Flask
from models import Administrators,AirlineCompanies,Countries,Customers,Tickets,UserRoles,Users,Flights  # Import your models
from database import Session
from repository import Repository


def configure_routes(app:Flask):
    
    @app.route('/users', methods=['GET'])
    def get_all_test():
        session = Session()
        repo = Repository(session)
        users = repo.get_all(Users)
        session.close()
        return render_template('users.html',users=users)
    
    @app.route('/user_roles', methods=['GET'])
    def roles():
        session = Session()
        repo = Repository(session)
        user_roles = repo.get_all(UserRoles)
        session.close()
        return render_template('user_roles.html', user_roles=user_roles)
    
    @app.route('/airlines', methods=['GET'])
    def airlines():
        session = Session()
        repo = Repository(session)
        airlines = repo.get_all(AirlineCompanies)
        session.close()
        return render_template('airlines.html', airlines=airlines)
    
    
#region Area of web display
    @app.route('/test', methods=['GET'])
    def placeholder_displays():
        session = Session()
        repo = Repository(session)
        test = repo.get_user_by_username('ronasor')
        data = json_formatter(test)
        session.close()
        return data
        #working for get_user_by_username('username')
    @app.route('/test1', methods=['GET'])
    def placeholder_displays2():
        session = Session()
        repo = Repository(session)
        test_result = repo.get_tickets_by_customer(3)
        data = json_formatter(test_result)
        session.close()
        return jsonify(data)
        #working for get_tickets_by_customer(customer_id:int)
    
    
    
    
   


    @app.route('/create_customer', methods=['POST'])
    def create_customer():
        try:
            # Get parameters from the request URL
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            address = request.form.get('address')
            phone_no = request.form.get('phone_no')
            credit_card_no = request.form.get('credit_card_no')
            user_id = request.form.get('user_id')
            app.logger.info(f"Received data: {first_name}, {last_name}, {address}, {phone_no}, {credit_card_no}, {user_id}")

            # Validate the presence of required parameters
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
            # Add the new customer to the database using the class method
            repo = Repository(session=session_instance)
            result = repo.add(new_customer)
            if result:
                return jsonify({"message": "Customer created successfully"}), 201
            else:
                return jsonify({"message":"The entry either already exist or data provided is incorrect"}),418
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            return jsonify({"error": str(e)}), 500
        
        
    @app.route('/delete_customer', methods=['POST'])
    def delete_customer():
        try:
            # Get parameters from the request URL
            id = request.form.get('id')
           
            #app.logger.info(f"Received data: {first_name}, {last_name}, {address}, {phone_no}, {credit_card_no}, {user_id}")

            # Validate the presence of required parameters
            if not id:
                app.logger.error("Incomplete data provided")
                return jsonify({"error": "Incomplete data provided"}), 400

            # Logic to create a new customer instance and save it to the database...
            session_instance = Session()
            # Add the new customer to the database using the class method
            repo = Repository(session=session_instance)
            customer = repo.get_by_id(Customers,id)
            repo.remove(customer)
            return jsonify({"message": "Customer removed successfully"}), 201
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            return jsonify({"error": str(e)}), 500
        
        
    @app.route('/delete', methods=['POST'])
    def delete():
        try:
            # Get parameters from the request URL
            id = request.form.get('id')
            tablename = request.form.get('tablename')

            # Define the list of table names
            tablenames = ['administrators', 'airline_companies', 'countries', 'customers', 'tickets', 'user_roles', 'users', 'flights']

            # Check if the provided tablename is valid
            if tablename.lower() not in tablenames:
                return jsonify({"error": "Invalid tablename"}), 400

            # Import the necessary model dynamically based on the tablename
            model = globals()[tablename.capitalize()]
            # Delete the record from the database
            session = Session()
            repo = Repository(session=session)
            result = repo.remove(model,id)
            if result:
                return jsonify({"message": "Record deleted successfully"}), 200
            else:
                return jsonify(''),204
        except Exception as e:
            return jsonify({"error": str(e)}), 500

#endregion

    def json_formatter(cursor):
            result = cursor.fetchall()
            columns = cursor.keys()
            data = [dict(zip(columns, row)) for row in result] 
            return data
            
        

    if __name__ == '__main__':
        app.run(debug=True)

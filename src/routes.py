'''
Module used for better organized routing of flask app to endpoints
'''
from flask import render_template,jsonify
from models import Administrators,AirlineCompanies,Countries,Customers,Tickets,UserRoles,Users  # Import your models
from database import Session
from repository import Repository


def configure_routes(app):
    @app.route('/roles', methods=['GET'])
    def roles():
        session = Session()
        repo = Repository(session)
        user_roles = repo.get_all(UserRoles)
        session.close()
        return render_template('roles.html', user_roles=user_roles)
    
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
        data = vibrator(test)
        session.close()
        return data
        #working for get_user_by_username('username')
    @app.route('/test1', methods=['GET'])
    def placeholder_displays2():
        session = Session()
        repo = Repository(session)
        test_result = repo.get_tickets_by_customer(3)
        data = vibrator(test_result)
        session.close()
        return jsonify(data)
        #working for get_tickets_by_customer(customer_id:int)
    
    
    def vibrator(cursor):
        result = cursor.fetchall()
        columns = cursor.keys()
        data = [dict(zip(columns, row)) for row in result] 
        return data
#endregion
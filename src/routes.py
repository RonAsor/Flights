'''
Module used for better organized routing of flask app to endpoints
'''
from flask import render_template
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
    
    @app.route('/test', methods=['GET'])
    def test():
        session = Session()
        repo = Repository(session)
        test = repo.get_user_by_username('ronasor')
        session.close()
        return test
        #working for get_user_by_username('username')
    @app.route('/test1', methods=['GET'])
    def test1():
        session = Session()
        repo = Repository(session)
        test = repo.get_tickets_by_customer(1)
        session.close()
        return test
        #working for get_tickets_by_customer(customer_id:int)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from configparser import ConfigParser
from time import sleep
from tools.logger import SingletonLogger

#Initialize flask app, and config from config.cfg file
app = Flask(__name__)


config = ConfigParser()
config.read('config.cfg')

if 'SQLALCHEMY_DATABASE_URI' in config['DATABASE']:
    app.config.update(config['DATABASE'].items())
    app.config = {key.upper(): value for key, value in app.config.items()}
db = SQLAlchemy(app)
log = SingletonLogger()

    
if __name__=="__main__":
    log.get_logger().info('Attempting to start the server...')
    app.run(debug=True)
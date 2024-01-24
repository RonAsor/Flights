# app.py
from flask import Flask
from configparser import ConfigParser
from tools.logger import SingletonLogger
from routes import configure_routes
from database import engine  

app = Flask(__name__)

config = ConfigParser()
config.read('config.cfg')

log = SingletonLogger()

# Configure routes from the separate file
configure_routes(app)

if __name__ == "__main__":
    log.get_logger().info('Attempting to start the server...')
    app.run(debug=True)

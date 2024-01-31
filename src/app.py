# app.py
from flask import Flask
from src.tools.logger import SingletonLogger
from src.routes import configure_routes
from src.database import engine  

app = Flask(__name__)


log = SingletonLogger()

# Configure routes from the separate file
configure_routes(app)

if __name__ == "__main__":
    log.get_logger().info('Attempting to start the server...')
    app.run(debug=True)


##db.createall
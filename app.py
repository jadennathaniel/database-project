from flask import Flask
from config import Config
import mysql.connector
from models import create_tables

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'

def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

def initialize_database():
    create_tables()

from routes import *

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)


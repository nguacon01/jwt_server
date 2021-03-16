from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restful import Api
import sqlalchemy

api = Api()
jwt = JWTManager()
cors = CORS()
sqlalchemy = SQLAlchemy()
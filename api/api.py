from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import cached_property
from flask_restful import Api, reqparse
from flask_restful_swagger import swagger
from api.setting import ConfigServise

from flask_migrate import Migrate


from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

#### Aplication ####
application = Flask(__name__)
application.config.from_object(ConfigServise)

#### Docummentation ####
api_application = swagger.docs(Api(application), apiVersion='1.1')

#### JWTOKENS ####
jwt = JWTManager(application)

#### DataBase ####
db = SQLAlchemy(application)

#### Migrations ####

migrate = Migrate(application, db)


#### Routs #####
from api.urls import UrlManager
UrlManager(application, api_application)



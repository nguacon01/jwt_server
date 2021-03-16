from flask import Flask, jsonify
from flask_jwt_extended.utils import create_access_token, get_jwt_identity, set_access_cookies
from flask_restful import Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, get_raw_jwt
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///app.db'
app.config["SECRET_KEY"] = 'acfsdfsdfsdfsdfs'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_TOKEN_LOCATION"] = ["headers"]


api = Api(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)
cors = CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.before_first_request
def create_db():
    db.create_all()


import resources
api.add_resource(resources.UserLogin,'/api/login')
api.add_resource(resources.UserLogoutAccess,'/api/logout/access')
api.add_resource(resources.UserLogoutRefresh,'/api/logout/refresh')
api.add_resource(resources.UserRegistration,'/api/registration')
api.add_resource(resources.AllUsers,'/api/users')
api.add_resource(resources.SecretResource,'/api/secret')


from models import RevokedTokenModel
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_jti_blacklisted(jti)

# refresh any token in incoming request if it will be expired in 30 minutes
@app.after_request
def refresh_expired_token(response):
    try:
        exp_timestamp = get_raw_jwt()['exp']
        now = datetime.now(timezone.utc)
        target_timestam = datetime.timestamp(now+timedelta(minutes=30))
        if target_timestam > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response=response, encoded_access_token=access_token)
            return response
    except:
        return response

@app.route('/')
def index():
    return jsonify({'message':'API page'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9999', debug=True)
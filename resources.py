from flask.globals import request
from flask_restful import Resource, reqparse
from models import UserModel, RevokedTokenModel
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required
from flask_jwt_extended import jwt_refresh_token_required, get_jwt_identity, get_raw_jwt
from flask_jwt_extended import set_access_cookies, set_refresh_cookies
from flask import jsonify
import re
import json

def validate_email(email):
    regex_email = re.compile('^[a-z0-9A-Z._%+-]+@[A-Z0-9a-z.-]+\.[A-Za-z]{2,}$')
    if not re.match(pattern=regex_email, string=email):
        return False
    return True

class UserRegistration(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', help="Email is required", required=True)
        self.parser.add_argument('password', help="Password is required", required=True)
        self.parser.add_argument('username')
    def post(self):
        data = self.parser.parse_args()
        regex_email = re.compile('^[a-z0-9A-Z._%+-]+@[A-Z0-9a-z.-]+\.[A-Za-z]{2,}$')
        if not validate_email(data['email']):
            return {"message":f"{data['email']} is not in form of a regular email"}, 401

        if UserModel.find_user_by_email(email=data['email']):
            return {"message":f"Email {data['email']} already exists"}, 401

        new_user = UserModel(
            email = data['email'],
            password = UserModel.generate_hash(data['password']),
            username = data['username']
        )
        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=data['email'])
            refresh_token = create_refresh_token(identity=data['email'])
            
            response = jsonify({
                "message":f"User {data['email']} was created",
                "access_token":access_token,
                "refresh_token":refresh_token
            })
            # set_access_cookies(response=response, encoded_access_token=access_token)
            # set_refresh_cookies(response=response, encoded_refresh_token=refresh_token)
            return response
        except:
            return jsonify({'message': 'Something went wrong'})
            

class UserLogin(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', help="Email is required", required=True)
        self.parser.add_argument('password', help="Password is required", required=True)
    def post(self):
        data = self.parser.parse_args()
        email = data['email']
        if not validate_email(email=email):
            return {"message":f"{email} is not in form of a regular email"}, 401
        current_user = UserModel.find_user_by_email(email)
        if not current_user:
            return {"message":f"Email {data['email']} does not exist"}, 401
        if UserModel.verify_hash(password=data['password'], hashed=current_user.password):
            access_token = create_access_token(identity=data['email'])
            refresh_token = create_refresh_token(identity=data['email'])
            response = jsonify({
                "message":f"Logged in as {data['email']}",
                "access_token":access_token,
                "refresh_token":refresh_token
            })
            # set_access_cookies(response=response, encoded_access_token=access_token)
            # set_refresh_cookies(response=response, encoded_refresh_token=refresh_token)
            return response
        else:
            return {"message":"Wrong Credentials"}, 401

      
class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            response = jsonify({"message":"Access token has been revoked"})
            return response
        except:
            response = jsonify({"message":"Access token revoking went wrong"})
            return response
      
      
class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            response = jsonify({"message":"Refresh token has been revoked"})
            return response
        except:
            response = jsonify({"message":"Refresh token revoking went wrong"})
            return response
      
      
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        response = jsonify({'message': 'Token has been refreshed'})
        set_access_cookies(response=response, encoded_access_token=access_token)
        return response
      
      
class AllUsers(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('user_id', help="User Id is required", required=True)
    @jwt_required
    def get(self):
        return UserModel.return_all()

    def delete(self):
        data = self.parser.parse_args()

        if 'user_id' in data:
            if UserModel.delete_one(id=data['user_id']):
                return {"message":"User has been removed"}, 200
            else: return {"message":"Fail"}, 401
        return UserModel.delete_all()
      

class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'answer': 42
        }, 200
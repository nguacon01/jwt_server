from sqlalchemy.dialects.postgresql import UUID
import uuid
from wsgi import db
import bcrypt
from sqlalchemy.inspection import inspect

class Serializer(object):
    # convert an object to a dict
    def serialize(self):
        dict = {}
        for c in inspect(self).attrs.keys():
            key = c
            val = getattr(self, c)
            if isinstance(val, bytes):
                val = val.decode()
            dict[key] = val
        return dict
    
    @staticmethod
    def serialize_list(list):
        return {
            'data' : [item.serialize() for item in list]
        }

class General(db.Model, Serializer):
    __abstract__ = True
    """
    Class general has functions general like: add, remove, update, read
    """

    @classmethod
    def return_one(cls, param, as_model=False):
        """
            return a object or a dict of object
            param: {'col':col_name, 'value':value_of_col}
        """
        try:
            col_name = getattr(cls, param['col'])
            data = db.session.query(cls).filter(col_name == param['value']).first()
            if as_model == False:
                return data.serialize()
            else:
                return data
        except Exception as e:
            print(e)
            raise

    @classmethod
    def return_all(cls, columns=None, params = None, order_by=None, order='asc', as_model=False):
        """
            return a dictionary of objects from a model
            colums: list of columns that we want to get
            params: dict of filter [{'col':name of column want to filter, 'filter': value to filter}]
            as_model: if True, return a object of model. If False, return a dict
        """
        query = db.session.query(cls)
        if params:
            for param in params:
                col_name = getattr(cls, param['col'])
                query = query.filter(col_name == param['filter'])
        if order_by:
            order_col = getattr(cls, order_by)
            if order=="asc":
                order_col.asc()
            else:
                order_col.desc()
            query = query.order_by(order_col)
        data = query.all()
        if as_model:
            # return list of object
            return data
        else:
            # return dict
            return General.serialize_list(data)

    @classmethod
    def add_one(cls, entity_dict):
        try:
            model = cls(**entity_dict)
            db.session.add(model)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            db.session.rollback()
            raise
    
    @classmethod
    def add_many(cls, list_items):
        if not isinstance(list_items, list):
            return False
        for item_entity_dict in list_items:
            General.add_one(item_entity_dict)
        return True

    @classmethod
    def delete_one(cls, id):
        try:
            db.session.delete(db.session.query(cls).get(id))
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            db.session.rollback()
            raise
    
    @classmethod
    def delete_all(cls):
        try:
            num_rows = db.session.query(cls).delete()
            db.session.commit()
            return num_rows
        except Exception as e:
            print(e)
            db.session.rollback()
            return False

    @classmethod
    def update_one(cls, entity_dict):
        try:
            model = cls(**entity_dict)
            db.session.merge(model)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            db.session.rollback()
            raise

    @classmethod
    def update_all(cls, list_of_items):
        if not isinstance(list_of_items, list):
            return False
        for item_entity_dict in list_of_items:
            General.update_one(item_entity_dict)
        return True

class UserModel(General):
    __tablename__ = 'users'
    id = db.Column(db.String(120), primary_key=True, default=uuid.uuid4().__str__)
    username = db.Column(db.String(120), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    @staticmethod
    def generate_hash(password):
        return bcrypt.hashpw(password=password.encode(), salt=bcrypt.gensalt())
    @staticmethod
    def verify_hash(password, hashed):
        return bcrypt.checkpw(password.encode(), hashed)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_user_by_email(cls, email):
        # return cls.query.filter_by(email=email).first()
        return cls.return_one({'col':'email', 'value':email}, as_model=True)

    # @classmethod
    # def return_all(cls):
    #     def to_json(x):
    #         return {
    #             'email':x.email,
    #             'password':x.password.decode()
    #         }
    #     return {
    #         'users': list(map(lambda x: to_json(x), UserModel.query.all()))
    #     }

    @classmethod
    def delete_all(cls):
        try:
            num_row_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {"message":f"{num_row_deleted} row(s) was deleted"}
        except:
            return{"message":"Something went wrong"}, 500

class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
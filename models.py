from datetime import datetime, timedelta

import jwt
from flask import current_app
from sqlalchemy.orm import relationship

from app import db
from sqlalchemy.dialects.postgresql import JSON

from flask_bcrypt import Bcrypt


class User(db.Model):

    __tablename__ = 'users'

    # Define the columns of the users table, starting with the primary key
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()

    def password_is_valid(self, password):

        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """Save a user to the database.
        This includes creating a new user and editing one.
        """
        db.session.add(self)
        db.session.commit()

    def generate_token(self, user_id):
        """ Generates the access token"""
        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=5),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                str(current_app.config.get('SECRET')),
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Authorization header."""
        try:
            # try to decode the token using our SECRET variable
            payload = jwt.decode(token, str(current_app.config.get('SECRET')))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"





db.Model.metadata.reflect(db.engine)


class Country(db.Model):
    __table__ = db.Model.metadata.tables['country']
    country_capital = relationship("City", cascade="all,delete", backref="country")

    def __repr__(self):
        return self.name


    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'code': self.code,
            'name': self.name,
            'continent': self.continent,
            'region': self.region,
            'indepyear': self.indepyear,
            'population': self.population,
            'localname': self.localname,
            'governmentform': self.governmentform,
            'headofstate': self.headofstate,
            'capital': self.capital,
            'code2': self.code2
        }

    @property
    def serializeregion(self):
        """Return object data in easily serializable format"""
        return {
            'region': self.region,
        }


    @property
    def serializecontinent(self):
        """Return object data in easily serializable format"""
        return {
            'continent': self.continent,
        }


class City(db.Model):
    __table__ = db.Model.metadata.tables['city']

    def __repr__(self):
        return self.name


    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'countrycode': self.countrycode,
            'district': self.district,
            'population': self.population
        }


class CountryLanguage(db.Model):
    __table__ = db.Model.metadata.tables['countrylanguage']

    def __repr__(self):
        return self.name


    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'countrycode': self.countrycode,
            'language': self.language,
            'countrycode': self.countrycode,
            'isofficial': self.isofficial,
            'percentage': self.percentage
        }



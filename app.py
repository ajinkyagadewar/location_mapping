from functools import wraps

from flask import Flask, jsonify, make_response
from flask import request
from flask.views import MethodView
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/world_data"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

from auth import auth_blueprint

app.register_blueprint(auth_blueprint)

from flask_restful import Resource, Api
from models import Country, City, CountryLanguage, User

api = Api(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        token = access_token.split(" ")[1]
        if not token:
            return jsonify({'message': 'token is missing!'}), 403
        try:
            user_id = User.decode_token(token)
            if isinstance(user_id, str):
                return jsonify({'message': 'please use updated token'}), 403
        except:
            return jsonify({'message': 'token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated


class RegionSearch(Resource):
    @token_required
    def get(self):
        search_term = request.args['continent']
        query = db.session.query(Country.region.distinct().label("region"))
        result = [row.region for row in query.filter_by(continent=search_term)]
        return jsonify(result)


api.add_resource(RegionSearch, '/api/region/')


class ContinentSearch(Resource):
    @cross_origin()
    @token_required
    def get(self):
        query = db.session.query(Country.continent.distinct().label("continent"))
        result = [row.continent for row in query.all()]
        return jsonify(result)


api.add_resource(ContinentSearch, '/api/continents/')


class SearchCountry(Resource):
    @cross_origin()
    @token_required
    def get(self):
        search_term = request.args['region']
        result = Country.query.filter_by(region=search_term)
        return jsonify([i.serialize for i in result])


api.add_resource(SearchCountry, '/api/country/')


class GetCountry(Resource):
    @cross_origin()
    @token_required
    def get(self):
        search_term = request.args['country_code']
        result = Country.query.filter_by(code=search_term)
        return jsonify([i.serialize for i in result])


api.add_resource(GetCountry, '/api/getcountry/')


class SearchCity(Resource):
    @token_required
    def get(self):
        search_term = request.args['country_code']
        result = City.query.filter_by(countrycode=search_term)
        return jsonify([i.serialize for i in result])


api.add_resource(SearchCity, '/api/city/')


class SearchDistrict(Resource):
    @token_required
    def get(self):
        search_term = request.args['country_code']
        query = db.session.query(City.district.distinct().label("district"))
        result = [row.district for row in query.filter_by(countrycode=search_term)]
        return jsonify(result)


api.add_resource(SearchDistrict, '/api/district/')


class SearchCountryLanguage(Resource):
    @token_required
    def get(self):
        search_term = request.args['country_code']
        result = CountryLanguage.query.filter_by(countrycode=search_term)
        return jsonify([i.serialize for i in result])


api.add_resource(SearchCountryLanguage, '/api/countrylanguage/')


class DeleteCity(Resource):
    @token_required
    def delete(self, id):
        city = City.query.get(id)
        if city:
            db.session.delete(city)
            db.session.commit()
            return {"message": "City was deleted successfully!"}, 200
        else:
            return {"message": "The City does not exist"}, 404

    @token_required
    def get(self, id):
        city = City.query.get(id)
        if city:
            results = city_serilize(city)
            return jsonify(results)

        else:
            return {"message": "The City does not exist"}, 404


api.add_resource(DeleteCity, '/api/cities/<id>')
from sqlalchemy import func


class Cities(Resource):
    @token_required
    def post(self):
        if request.is_json:
            data = request.get_json()
            id = data.get('id')
            if id:
                city = City.query.get(data['id'])
                city.countrycode = data['countrycode']
                city.name = name = data['name']
                city.district = data['district']
                city.population = data['population']
                db.session.commit()
                results = city_serilize(city)
                return {"message": "City has been created successfully.", "city": results}

            else:
                result = db.session.query(func.max(City.id).label('ml')).subquery()
                users = db.session.query(City).join(result, result.c.ml == City.id).first()

                city = City(id=users.id + 1, name=data['name'], countrycode=data['countrycode'],
                            district=data['district'],
                            population=data['population'])
                db.session.add(city)
                db.session.commit()
                results = city_serilize(city)
                return {"message": "City has been created successfully.", "city": results}


        else:
            return {"error": "The request payload is not in JSON format"}


api.add_resource(Cities, '/api/allCities/')


def city_serilize(city):
    results = [
        {
            'id': city.id,
            'name': city.name,
            'countrycode': city.countrycode,
            'district': city.district,
            'population': city.population
        }]
    return results


class RegistrationView(Resource):

    def post(self):
        data = request.get_json()
        # Query to see if the user already exists
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            # There is no user so we'll try to register them
            try:
                post_data = data
                # Register the user
                email = post_data['email']
                password = post_data['password']
                user = User(email=email, password=password)
                user.save()
                return {"message": "You registered successfully. Please log in.."}, 201

            except Exception as e:
                # An error occured, therefore return a string message containing the error
                response = {
                    'message': str(e)
                }
                return {"message": str(e)}, 401
        else:

            return {"message": "User already exists. Please login."}, 202


api.add_resource(RegistrationView, '/api/auth/register')


class LoginView(MethodView):

    @cross_origin()
    def post(self):
        """Handle POST request for this view. Url ---> /auth/login"""
        try:
            # Get the user object using their email (unique to every user)
            data = request.get_json()
            user = User.query.filter_by(email=data['email']).first()
            # Try to authenticate the found user using their password
            if user and user.password_is_valid(data['password']):
                # Generate the access token. This will be used as the authorization header
                access_token = user.generate_token(user.id)
                if access_token:
                    return {"message": "You logged in successfully.", "access_token": access_token.decode()}, 200

            else:
                # User does not exist. Therefore, we return an error message
                return {"message": "Invalid email or password, Please try again"}, 401

        except Exception as e:
            # Create a response containing an string error message
            response = {
                'message': str(e)
            }
            # Return a server error using the HTTP Error Code 500 (Internal Server Error)
            return make_response(jsonify(response)), 500


api.add_resource(LoginView, '/api/auth/login')


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)

from . import auth
from .errors import not_found
from .errors import unauthorized, bad_request
from flask import request, jsonify
from flask_login import login_user, logout_user
from app import db
from app.models import User, Passenger, Driver
from ..api_1_0.authentication import auth as auth_head


@auth.route('/passenger_register', methods=['POST'])
def passenger_register():
    phone_number = request.json.get('phone_number')
    username = request.json.get('username')
    password = request.json.get('password')
    is_confirmed = request.json.get('is_confirmed')
    passenger = Passenger.query.filter_by(phone_number=phone_number).first()
    if passenger:
        return bad_request('Phone number already in use.')
    passenger = Passenger.query.filter_by(username=username).first()
    if passenger:
        return bad_request('Username already in use.')
    passenger = Passenger(phone_number=phone_number, username=username, password=password, is_confirmed=is_confirmed)
    db.session.add(passenger)
    db.session.commit()
    response = jsonify({'message': 'Successful registration.'})
    response.status_code = 201
    return response


@auth.route('/driver_register', methods=['POST'])
def driver_register():
    phone_number = request.json.get('phone_number')
    username = request.json.get('username')
    password = request.json.get('password')
    is_confirmed = request.json.get('is_confirmed')
    driver = Driver.query.filter_by(phone_number=phone_number).first()
    if driver:
        return bad_request('Phone number already in use.')
    driver = Driver.query.filter_by(username=username).first()
    if driver:
        return bad_request('Username already in use.')
    driver = Driver(phone_number=phone_number, username=username, password=password, is_confirmed=is_confirmed)
    db.session.add(driver)
    db.session.commit()
    response = jsonify({'message': 'Successful registration.'})
    response.status_code = 201
    return response


@auth.route('/passenger_login', methods=['GET', 'POST'])
def passenger_login():
    phone_number = request.json.get('phone_number')
    password = request.json.get('password')
    passenger = Passenger.query.filter_by(phone_number=phone_number).first()
    if not passenger:
        return unauthorized('Invalid phone_number or password.')
    token = passenger.generate_auth_token(3600)
    token = bytes.decode(token)
    if passenger.verify_password(password):
        login_user(passenger)
        response = jsonify({'message': 'Successful login.',
                            'passenger_id': passenger.id,
                            'token': token,
                            'expiration': 3600})
        response.status_code = 200
        return response
    return unauthorized('Invalid phone_number or password.')


@auth.route('/driver_login', methods=['GET', 'POST'])
def driver_login():
    phone_number = request.json.get('phone_number')
    password = request.json.get('password')
    driver = Driver.query.filter_by(phone_number=phone_number).first()
    if not driver:
        return unauthorized('Invalid phone_number or password.')
    token = driver.generate_auth_token(3600)
    token = bytes.decode(token)
    if driver.verify_password(password):
        login_user(driver)
        response = jsonify({'message': 'Successful login.',
                            'driver_id': driver.id,
                            'token': token,
                            'expiration': 3600})
        response.status_code = 200
        return response
    return unauthorized('Invalid username or password.')


@auth.route('/passenger_logout/<int:passenger_id>', methods=['POST'])
def passenger_logout(passenger_id):
    passenger = Passenger.query.filter_by(id=passenger_id)
    if not passenger:
        return not_found('Passenger not found.')
    logout_user()
    response = jsonify({'message': 'Successful logout'})
    response.status_code = 200
    return response


@auth.route('/driver_logout/<int:driver_id>', methods=['POST'])
def driver_logout(driver_id):
    driver = Driver.query.filter_by(id=driver_id)
    if not driver:
        return not_found('Passenger not found.')
    logout_user()
    response = jsonify({'message': 'Successful logout'})
    response.status_code = 200
    return response

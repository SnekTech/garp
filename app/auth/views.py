from . import auth
from .errors import unauthorized, bad_request
from flask import request, jsonify
from flask_login import login_user
from app import db
from app.models import User
from ..api_1_0.authentication import auth as auth_head


@auth.route('/register', methods=['POST'])
def register():
    response = jsonify({'message': 'Successful registration.'})
    response.status_code = 201

    phone_number = request.json.get('phone_number')
    username = request.json.get('username')
    password = request.json.get('password')
    is_confirmed = request.json.get('is_confirmed')
    user = User.query.filter_by(phone_number=phone_number).first()
    if user:
        return bad_request('Phone number already in use.')
    user = User.query.filter_by(username=username).first()
    if user:
        return bad_request('Username already in use.')
    user = User(phone_number=phone_number, username=username, password=password, is_confirmed=is_confirmed)
    db.session.add(user)
    db.session.commit()
    return response


@auth.route('/login')
@auth_head.login_required
def login():
    phone_number = request.args.get('phone_number')
    password = request.args.get('password')
    user = User.query.filter_by(phone_number=phone_number).first()
    token = user.generate_auth_token(3600)
    token = bytes.decode(token)
    if user is not None and user.verify_password(password):
        login_user(user)
        response = jsonify({'message': 'Successful login.',
                            'token': token,
                            'expiration': 3600})
        response.status_code = 200
        return response
    return unauthorized('Invalid username or password.')


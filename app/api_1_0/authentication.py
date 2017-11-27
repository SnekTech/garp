from flask_httpauth import HTTPBasicAuth
from flask import g, jsonify
from app.models import AnonymousUser, User, Passenger, Driver
from .errors import unauthorized, forbidden
from . import api
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(number_or_token, password):
    print('123', number_or_token)
    if number_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        token = str.encode(number_or_token)
        g.current_user = User.verify_auth_token(token)
        print(g.current_user.username)
        g.token_used = True
        return g.current_user is not None
    # user = User.query.filter_by(phone_number=number_or_token).first()
    # if not user:
    #     return False
    # g.current_user = user
    # g.token_used = False
    user = Passenger.query.filter_by(phone_number=number_or_token).first() \
           or Driver.query.filter_by(phone_number=number_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


# @api.before_request
# @auth.login_required
# def before_request():
#     if g.current_user.is_anonymous:
#         print('forbidden')
#         return forbidden('Anonymous user.')
#     elif not g.current_user.is_confirmed:
#         return forbidden('Unconfirmed account.')


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    token = g.current_user.generate_auth_token(expiration=3600)
    token_string = bytes.decode(token)
    return jsonify({'token': token_string,
                    'expiration': 3600})

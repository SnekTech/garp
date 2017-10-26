from . import api
from app.models import User
from flask import jsonify


@api.route('/users/<phone_number>')
def get_user(phone_number):
    user = User.query.filter_by(phone_number=phone_number).first()
    return jsonify(user.to_json())

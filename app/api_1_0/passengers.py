from . import api
from .. import db, utils
from .authentication import auth
from .errors import not_found
from app.models import Passenger, Driver
from flask import jsonify, request


# 获取单个乘客的信息
@api.route('/passengers/<int:passenger_id>')
def get_passenger(passenger_id):
    passenger = Passenger.query.get_or_404(passenger_id)
    return jsonify(passenger.to_json()), 200


# 获取和更新单个乘客的坐标
@api.route('/passenger_location/<int:passenger_id>', methods=['GET', 'POST'])
def passenger_location(passenger_id):
    passenger = Passenger.query.filter_by(id=passenger_id).first()
    if not passenger:
        return not_found('Passenger not found.')
    if request.method == 'GET':
        response = jsonify({'passenger_id': passenger.id,
                            'location': passenger.location})
        response.status_code = 200
        return response
    else:
        location = request.json.get('location')
        passenger.location = location
        db.session.add(passenger)
        response = jsonify({'passenger_id': passenger.id,
                            'location': passenger.location})
        response.status_code = 200
        return response


@api.route('/ride_request/<int:passenger_id>', methods=['POST'])
def ride_request(passenger_id):
    passenger = Passenger.query.get_or_404(passenger_id)
    driver = utils.choose_driver(passenger)
    if driver:
        return jsonify({'driver_id': driver.id}), 200
    else:
        return not_found('No drivers available.')

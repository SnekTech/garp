from ..models import Driver, Passenger
from .. import db
from . import api
from .errors import not_found
from flask import jsonify, request


# 获取单个司机的信息
@api.route('/drivers/<int:driver_id>')
def get_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    return jsonify(driver.to_json()), 200


# 获取和更新单个司机的坐标
@api.route('/driver_location/<int:driver_id>', methods=['GET', 'POST'])
def driver_location(driver_id):
    driver = Driver.query.filter_by(id=driver_id).first()
    if not driver:
        return not_found('Driver not found.')
    if request.method == 'GET':
        response = jsonify({'driver_id': driver.id,
                            'location': driver.location})
        response.status_code = 200
        return response
    else:
        location = request.json.get('location')
        driver.location = location
        db.session.add(driver)
        response = jsonify({'driver_id': driver.id,
                            'location': driver.location})
        response.status_code = 201
        return response


@api.route('/driver_check/<int:driver_id>')
def driver_check(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    if driver.current_aiming_passenger_id:
        passenger = Passenger.query.filter_by(id=driver.current_aiming_passenger_id).first()
        return jsonify({'status': 'picking',
                        'destination': passenger.location,
                        'current_aiming_passenger_id': passenger.id}), 200
    elif driver.final_destination:
        return jsonify({'status': 'heading',
                        'destination': driver.final_destination}), 200
    return not_found('No requests yet.')

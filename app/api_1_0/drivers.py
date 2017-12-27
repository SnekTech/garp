from ..models import Driver, Passenger, Order
from .. import db
from . import api
from .errors import not_found
from flask import jsonify, request, current_app
import os
import pickle


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
        response.status_code = 200
        return response


@api.route('/driver_check/<int:driver_id>')
def driver_check(driver_id):
    driver = Driver.query.get_or_404(driver_id)

    # 反序列化driver的passengers和destinations对象
    with open(os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_passengers.pkl'.format(driver.id)),
              'rb') as f:
        driver.passengers = pickle.load(f)
    with open(
            os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_destinations.pkl'.format(driver.id)),
            'rb') as f:
        driver.destinations = pickle.load(f)

    if driver.destinations:
        destination = driver.destinations[0]
        if destination[1] == 0:
            driver.picking = True
            driver.heading = False
        else:
            driver.picking = False
            driver.heading = True
        db.session.add(driver)
        db.session.commit()
        return jsonify({'picking': driver.picking,
                        'heading': driver.heading,
                        'destination': driver.destinations}), 200
    else:
        return not_found('No requests yet.')


@api.route('/get_on_confirm/<int:driver_id>', methods=['POST'])
def get_on_confirm(driver_id):
    driver = Driver.query.get(driver_id)
    driver.picking = False
    driver.heading = True

    # 反序列化
    with open(
            os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_destinations.pkl'.format(driver.id)),
            'rb') as f:
        driver.destinations = pickle.load(f)
    if driver.destinations:
        driver.destinations.pop(0)

        # 序列化
        with open(
                os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_destinations.pkl'.format(driver.id)),
                'wb') as f:
            pickle.dump(driver.destinations, f)

        return jsonify({'destination': driver.destinations}), 201


@api.route('/enable_drivers', methods=['POST'])
def enable_driver():
    # 云南省昆明市官渡区昆明火车站
    # boss
    # 102.721725, 25.015834
    #
    # 云南省昆明市呈贡区云南大学呈贡校区
    # 102.849703, 24.826861
    #
    # 云南省昆明市呈贡区云南大学呈贡校区图书馆
    # rabbit
    # 102.850828, 24.824721
    #
    # 云南省昆明市呈贡区公交枢纽
    # guoshuji
    # 102.839073, 24.901129
    #
    # 云南省昆明市呈贡区昆明市第三中学
    # rabbit2
    # 102.836785, 24.884822
    db.drop_all()
    db.create_all()
    driver1 = Driver(phone_number='15838289003', username='driver1', password='123', is_confirmed=True, remaining_seats=4)
    driver1.location = '102.848948,24.828688'
    driver2 = Driver(phone_number='123456789', username='driver2', password='123', is_confirmed=True, remaining_seats=4)
    driver2.location = '102.850828,24.824721'

    passenger1 = Passenger(phone_number='15087186168', username='passenger1', password='123', is_confirmed=True)
    passenger1.location = '102.850828,24.824721'
    passenger2 = Passenger(phone_number='15225185597', username='passenger2', password='123', is_confirmed=True)
    passenger2.location = '102.852289,24.824373'

    db.session.add(driver1)
    db.session.add(driver2)
    db.session.add(passenger1)
    db.session.add(passenger2)
    db.session.commit()
    order1 = Order(begin_location=passenger1.location, end_location='102.855005,24.825939', passenger_id=passenger1.id,
                   finished=False)
    order2 = Order(begin_location=passenger2.location, end_location='102.849703,24.826861', passenger_id=passenger2.id,
                   finished=False)

    db.session.add(order1)
    db.session.add(order2)
    db.session.commit()
    # 初始化driver_obj
    with open(
            os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_passengers.pkl'.format(driver1.id)),
            'wb') as f:
        pickle.dump([], f)
    with open(
            os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_destinations.pkl'.format(driver1.id)),
            'wb') as f:
        pickle.dump([], f)
    with open(
            os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_passengers.pkl'.format(driver2.id)),
            'wb') as f:
        pickle.dump([], f)
    with open(
            os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_destinations.pkl'.format(driver2.id)),
            'wb') as f:
        pickle.dump([], f)
    return jsonify({'available': 'All drivers are available.'}), 200


@api.route('/set_drivers_location', methods=['POST'])
def set_drivers_location():
    drivers = Driver.query.all()
    for driver in drivers:
        driver.location = '116,24'
        db.session.add(driver)
    db.session.commit()
    return jsonify({'message': 'All drivers locates at 116,24.'}), 200

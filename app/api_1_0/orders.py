from . import api
from app import db
from app.models import User, Passenger, Driver, Order
from flask import jsonify, request, url_for, current_app
import os
import pickle


@api.route('/orders/<int:order_id>')
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_json()), 200


@api.route('/new_order', methods=['POST'])
def new_order():
    order = Order.from_json(request.json)
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_json()), 200


@api.route('/pay/<int:order_id>', methods=['POST'])
def pay(order_id):
    order = Order.query.get_or_404(order_id)
    passenger = Passenger.query.filter_by(id=order.passenger_id).first()
    driver = Driver.query.filter_by(id=order.driver_id).first()

    # 反序列化
    with open(
            os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_passengers.pkl'.format(driver.id)),
            'rb') as f:
        driver.passengers = pickle.load(f)
    with open(
            os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_destinations.pkl'.format(driver.id)),
            'rb') as f:
        driver.destinations = pickle.load(f)

    print(driver.passengers)
    print(passenger)
    driver.passengers.remove(passenger.id)
    driver.destinations.pop(0)

    # 序列化
    with open(
            os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_passengers.pkl'.format(driver.id)),
            'wb') as f:
        pickle.dump(driver.passengers, f)
    with open(
            os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_destinations.pkl'.format(driver.id)),
            'wb') as f:
        pickle.dump(driver.destinations, f)

    # passenger.balance -= order.price
    # driver.balance += order.price
    driver.available = True
    driver.remaining_seats += 1
    order.finished = True

    db.session.add(driver)
    db.session.add(order)
    db.session.commit()
    return jsonify({'order_id': order.id,
                    'passenger_id': passenger.id,
                    'driver_id': driver.id,
                    'passenger_balance': passenger.balance,
                    'driver_balance': driver.balance}), 200

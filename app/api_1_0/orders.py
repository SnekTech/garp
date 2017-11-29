from . import api
from app import db
from app.models import User, Passenger, Driver, Order
from flask import jsonify, request, url_for


@api.route('/orders/<int:order_id>')
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_json()), 200


@api.route('/new_order', methods=['POST'])
def new_order():
    order = Order.from_json(request.json)
    driver = Driver.query.filter_by(id=order.driver_id).first()
    driver.current_aiming_passenger_id = None
    driver.final_destination = order.end_location
    db.session.add(order)
    db.session.add(driver)
    db.session.commit()
    return jsonify(order.to_json()), 200


@api.route('/pay/<int:order_id>', methods=['POST'])
def pay(order_id):
    order = Order.query.get_or_404(order_id)
    passenger = Passenger.query.filter_by(id=order.passenger_id).first()
    driver = Driver.query.filter_by(id=order.driver_id).first()

    passenger.balance -= order.price
    driver.balance += order.price
    driver.available = True
    order.finished = True

    db.session.add(passenger)
    db.session.add(driver)
    db.session.add(order)
    db.session.commit()
    return jsonify({'order_id': order.id,
                    'passenger_id': passenger.id,
                    'driver_id': driver.id,
                    'passenger_balance': passenger.balance,
                    'driver_balance': driver.balance}), 200

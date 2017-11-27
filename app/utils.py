from .models import Driver
from . import db
from flask import current_app
import requests


# 根据驾驶导航获取两点之间的距离（以用时最短为准）
def get_distance(origin, destination):
    origin_url = 'http://restapi.amap.com/v3/direction/driving'
    params = {'key': current_app.config['GARP_KEY'],
              'origin': origin,
              'destination': destination,
              }
    response = requests.get(origin_url, params=params)
    distance = response.json().get('route').get('paths')[0].get('distance')
    distance = int(distance)
    return distance


# 选取一个离乘客最近的可用司机
def choose_driver(passenger):
    driver_available = []
    for driver in Driver.query.all():
        if driver.remaining_seats != 0 and driver.available:
            driver_available.append(driver)
    if driver_available:
        selected_driver = driver_available[0]
    else:
        return None
    min_distance = get_distance(selected_driver.location, passenger.location)
    for driver in driver_available:
        temp = get_distance(driver.location, passenger.location)
        if temp < min_distance:
            selected_driver = driver
            min_distance = temp
    # 将该司机的状态变为不可用
    selected_driver.available = False
    selected_driver.current_aiming_passenger_id = passenger.id
    db.session.add(selected_driver)
    db.session.commit()
    return selected_driver

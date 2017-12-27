from .models import Driver, Passenger
from . import db
from flask import current_app
import requests
import itertools
import pickle
import os
from config import basedir


# 根据驾驶导航获取两点之间的距离（以用时最短为准）
def get_distance(origin, destination):
    origin_url = 'http://restapi.amap.com/v3/direction/walking'
    params = {'key': current_app.config['GARP_KEY'],
              'origin': origin,
              'destination': destination,
              }
    response = requests.get(origin_url, params=params)
    print(origin, destination)
    print(response.json())
    distance = response.json().get('route').get('paths')[0].get('distance')
    distance = int(distance)
    return distance


# 选取一个离乘客最近的可用司机
# 拼车算法，选取一个进行派单。若最近的司机是空车就直接返回，反之进行拼车可行性判断。
def choose_driver(passenger):
    driver_available = []
    for driver in Driver.query.all():
        if driver.remaining_seats != 0 and not driver.picking:
            driver_available.append(driver)

    while True:
        if driver_available:
            selected_driver = driver_available[0]
        else:
            return None
        print(driver_available)
        min_distance = get_distance(selected_driver.location, passenger.location)

        for driver in driver_available:
            temp = get_distance(driver.location, passenger.location)
            print(temp)
            if temp < min_distance:
                selected_driver = driver
                min_distance = temp
        print(driver_available)
        print(selected_driver)

        # 反序列化driver的passengers和destinations对象
        with open(os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_passengers.pkl'.format(selected_driver.id)),
                  'rb') as f:
            selected_driver.passengers = pickle.load(f)
        with open(
                os.path.join(current_app.config['DRIVER_OBJ'], 'driver_{}_destinations.pkl'.format(selected_driver.id)),
                'rb') as f:
            selected_driver.destinations = pickle.load(f)

        if not selected_driver.passengers:
            order = passenger.orders.filter_by(finished=False).first()
            selected_driver.passengers.append(passenger.id)
            selected_driver.destinations += [(order.begin_location, 0, passenger.id), (order.end_location, 1, passenger.id)]
            order.driver_id = selected_driver.id
            db.session.add(order)
            db.session.commit()

            # 序列化driver的passengers和destinations对象
            with open(os.path.join(current_app.config['DRIVER_OBJ'],
                                   'driver_{}_passengers.pkl'.format(selected_driver.id)),
                      'wb') as f:
                pickle.dump(selected_driver.passengers, f)
            with open(
                    os.path.join(current_app.config['DRIVER_OBJ'],
                                 'driver_{}_destinations.pkl'.format(selected_driver.id)),
                    'wb') as f:
                pickle.dump(selected_driver.destinations, f)
            print('空载司机')
            break
        else:
            order = passenger.orders.filter_by(finished=False).first()
            destinations = selected_driver.destinations + [(order.begin_location, 0, passenger.id), (order.end_location, 1, passenger.id)]
            p_destinations = list(itertools.permutations(destinations))
            remaining_indexes = []
            print(p_destinations)
            for p in p_destinations:
                p_list = list(p)
                if p_list.index((order.begin_location, 0, passenger.id)) < p_list.index((order.end_location, 1, passenger.id)):
                    remaining_indexes.append(p_destinations.index(p))
            print(remaining_indexes)
            new_p_destinations = []
            for i in remaining_indexes:
                new_p_destinations.append(p_destinations[i])
            p_destinations = new_p_destinations
            print(p_destinations)

            first_passenger = Passenger.query.get(selected_driver.passengers[0])
            first_order = first_passenger.orders.filter_by(finished=False).first()
            p_distances = []
            for i in range(len(p_destinations)):
                p_distances.append(0)

            # 排除使第一个乘客绕路的路线
            remaining_indexes = []
            origin_distance = get_distance(selected_driver.location, first_order.end_location)
            for i in range(len(p_distances)):
                p_distances[i] += get_distance(selected_driver.location, p_destinations[i][0][0])
                for j in range(len(p_destinations[i])-1):
                    p_distances[i] += get_distance(p_destinations[i][j][0], p_destinations[i][j+1][0])
                    if p_destinations[i][j+1][0] == first_order.end_location:
                        # 当计算到第一个乘客的下车点时停止累加
                        break
                print('{} - {} = {}'.format(p_distances[i], origin_distance, p_distances[i] - origin_distance))
                if p_distances[i] - origin_distance <= 2000:
                    # p_destinations.pop(i)
                    remaining_indexes.append(i)
            new_p_destinations = []
            for i in remaining_indexes:
                new_p_destinations.append(p_destinations[i])
            p_destinations = new_p_destinations
            print(p_destinations)

            # 如果有剩余的路线，从中选择一个总路程最小的
            if p_destinations:
                p_distances = []
                for i in range(len(p_destinations)):
                    p_distances.append(0)
                for i in range(len(p_distances)):
                    p_distances[i] += get_distance(selected_driver.location, p_destinations[i][0][0])
                    for j in range(len(p_destinations[i]) - 1):
                        p_distances[i] += get_distance(p_destinations[i][j][0], p_destinations[i][j + 1][0])

                min_distance = min(p_distances)
                selected_driver.passengers.append(passenger.id)
                order.driver_id = selected_driver.id
                db.session.add(order)
                db.session.commit()
                selected_driver.destinations = list(p_destinations[p_distances.index(min_distance)])
                with open(os.path.join(current_app.config['DRIVER_OBJ'],
                                       'driver_{}_passengers.pkl'.format(selected_driver.id)),
                          'wb') as f:
                    pickle.dump(selected_driver.passengers, f)
                with open(
                        os.path.join(current_app.config['DRIVER_OBJ'],
                                     'driver_{}_destinations.pkl'.format(selected_driver.id)),
                        'wb') as f:
                    pickle.dump(selected_driver.destinations, f)
                print('拼车')
                break
            else:
                print('拼车失败')
                print(selected_driver)
                print(driver_available)
                driver_available.remove(selected_driver)

    # 将该司机的状态变为不可用
    selected_driver.available = False
    selected_driver.remaining_seats -= 1
    # selected_driver.current_aiming_passenger_id = passenger.id
    db.session.add(selected_driver)
    db.session.commit()
    return selected_driver

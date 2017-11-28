from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from app.exceptions import ValidationError


@login_manager.user_loader
def load_user(user_id):
    passenger = Passenger.query.get(int(user_id))
    return Passenger.query.get(int(user_id)) or Driver.query.get(int(user_id))


# class Role(db.Model):
#     __tablename__ = 'roles'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64), unique=True)
#     users = db.relationship('User', backref='role', lazy='dynamic')
#
#     def __repr__(self):
#         return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(11), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    is_confirmed = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    x_position = db.Column(db.Integer, default=100)
    y_position = db.Column(db.Integer, default=200)

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # def generate_confirmation_token(self, expiration=3600):
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps({'confirm': self.id})
    #
    # def confirm(self, token):
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token)
    #     except:
    #         return False
    #     if data.get('confirm') != self.id:
    #         return False
    #     self.confirmed = True
    #     db.session.add(self)
    #     return True

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def to_json(self):
        json_user = {
            'username': self.username,
            'phone_number': self.phone_number,
            'is_confirmed': self.is_confirmed,
            'x_position': self.x_position,
            'y_position': self.y_position
        }
        return json_user


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class Passenger(UserMixin, db.Model):
    __tablename__ = 'passengers'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(11), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    is_confirmed = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    orders = db.relationship('Order', backref='passenger')
    driver = db.relationship('Driver', backref='current_aiming_passenger')

    # 余额
    balance = db.Column(db.Float, default=1000)

    location = db.Column(db.String(30), default='0.0,0.0')

    def __repr__(self):
        return '<Passenger %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return Driver.query.get(data['id'])

    def to_json(self):
        json_passenger = {
            'username': self.username,
            'phone_number': self.phone_number,
            'is_confirmed': self.is_confirmed,
            'balance': self.balance,
            'location': self.location,
        }
        return json_passenger


class Driver(UserMixin, db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(11), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    is_confirmed = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    orders = db.relationship('Order', backref='driver')

    # 余额
    balance = db.Column(db.Float, default=1000)

    car_id = db.Column(db.String(10), unique=True, index=True)
    remaining_seats = db.Column(db.Integer, default=4)
    available = db.Column(db.Boolean, default=True)
    current_aiming_passenger_id = db.Column(db.Integer, db.ForeignKey('passengers.id'), default=None)
    final_destination = db.Column(db.String(30), default=None)

    total_mileage = db.Column(db.Float, default=0)
    balance = db.Column(db.Float, default=0)

    location = db.Column(db.String(30), default='0.0,0.0')

    def __repr__(self):
        return '<Passenger %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return Driver.query.get(data['id'])

    def to_json(self):
        json_driver = {
            'driver_id': self.id,
            'username': self.username,
            'phone_number': self.phone_number,
            'is_confirmed': self.is_confirmed,
            'car_id': self.car_id,
            'remaining_seats': self.remaining_seats,
            'balance': self.balance,
            'mileage': self.total_mileage,
            'location': self.location,
        }
        return json_driver


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('passengers.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))
    begin_location = db.Column(db.String(30))
    end_location = db.Column(db.String(30))
    distance = db.Column(db.Float)
    price = db.Column(db.Float)

    finished = db.Column(db.Boolean, default=False)

    def to_json(self):
        json_order = {
            'order_id': self.id,
            'passenger_id': self.passenger_id,
            'driver_id': self.driver_id,
            'begin_location': self.begin_location,
            'end_location': self.end_location,
            'mileage': self.mileage,
            'price': self.price
        }
        return json_order

    @staticmethod
    def from_json(json_post):
        passenger_id = json_post.get('passenger_id')
        driver_id = json_post.get('driver_id')
        begin_location = json_post.get('begin_location')
        end_location = json_post.get('end_location')
        distance = json_post.get('distance')
        price = distance * current_app.config['PRICE_PER_KM']

        return Order(passenger_id=passenger_id, driver_id=driver_id,
                     begin_location=begin_location, end_location=end_location,
                     distance=distance, price=price)

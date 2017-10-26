import os
basedir = os.path.abspath(os.path.dirname(__file__))

# QQ邮箱授权码: bcub vkli ojie eadb
# 阿里云远程连接密码 444371


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    UPLOADED_PHOTOS_DEST = basedir
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    GARP_MAIL_SUBJECT_PREFIX = '[GARP]'
    GARP_MAIL_SENDER = 'GARP Admin <2654525303@qq.com>'
    # FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    GARP_ADMIN = os.environ.get('GARP_ADMIN') or '15087186168'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '2654525303@qq.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'bcubvkliojieeadb'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'mysql://root:@localhost:3306/garp?charset=utf8mb4'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'mysql://root:@localhost:3306/garp?charset=utf8mb4'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql://root:@localhost:3306/garp?charset=utf8mb4'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

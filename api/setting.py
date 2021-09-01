class ConfigServise(object):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://ubuntu:loky-hker.low@localhost:3306/flask_api'
    UPLOAD_FOLDER = '/home/ubuntu/flask_api/uploads/images'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    SECRET_KEY = 'API_FLASK'
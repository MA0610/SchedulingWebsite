from flask import Flask
from flask_pymongo import PyMongo
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sldadks lkjlkas'
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/scheduleWebsite'
    from .views import views
    from .auth import auth
    from .app import app
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')


    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'error'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models.user import User
    from app.views.auth import auth as auth_blueprint
    from app.controllers.inventory_controller import inventory as inventory_blueprint
    from app.controllers.reports_controller import reports as reports_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(inventory_blueprint)
    app.register_blueprint(reports_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
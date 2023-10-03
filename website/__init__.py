import os
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from .filters import nl2br 

db = SQLAlchemy()
DB_NAME = "database.db"
mail = Mail()


def create_app(testing=False):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.jinja_env.filters['nl2br'] = nl2br
    app.static_folder = 'static'
    
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # SMTP server address
    app.config['MAIL_PORT'] = 587  # Port for SMTP (587 is TLS, 465 is SSL)
    app.config['MAIL_USE_TLS'] = True  # Use TLS (True/False)
    app.config['MAIL_USE_SSL'] = False  # Use SSL (True/False)
    app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')
    
    mail = Mail(app)
    
    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_' + DB_NAME
        # postgres://dbcovered_user:nDeDhAgxOJqLe2Wl4Um1iiRgL6gtR6fo@dpg-cke4jl4gonuc73ani8eg-a.oregon-postgres.render.com/dbcovered
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    db.init_app(app)
    
    # change the app config files for sqlite 

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note, Skill
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app, mail

def create_database(app, testing=False):
    if testing:
        with app.app_context():
            db.drop_all()
            db.create_all()
    else:
        if not path.exists('website/' + DB_NAME):
            db.create_all(app=app)
            print('Created Database!')


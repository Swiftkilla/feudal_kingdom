from flask import Flask
from flask_login import LoginManager
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'super secret key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
loginMgr = LoginManager(app)
loginMgr.login_view = 'login'

from app import routes, models

if __name__ == '__main__':
    app.run(threaded=True, processes=2)

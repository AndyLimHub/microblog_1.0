from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_cors import CORS
import asyncio
import multiprocessing
from aiosmtpd.controller import Controller
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
CORS(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')    
    

def run_smtp():
    logging.basicConfig(level=logging.DEBUG)
    controller = Controller(None, hostname='localhost', port=1025)
    controller.start()

if __name__ == '__main__':
    # Start a separate process for the SMTP server
    smtp_process = multiprocessing.Process(target=run_smtp)
    smtp_process.start()

from app import routes, models, errors
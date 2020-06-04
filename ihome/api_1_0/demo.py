from . import api
from ihome import db, models
from flask import current_app

@api.route('/index/')
def index():
    current_app.logger.error('this is error')
    current_app.logger.info('this is info')
    current_app.logger.debug('this is debug')
    current_app.logger.warn('this is warn')
    return 'Index page'

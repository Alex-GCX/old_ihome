from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_wtf import CSRFProtect
from config import config_map
import redis
import logging
from logging.handlers import RotatingFileHandler

# 创建数据库对象
db = SQLAlchemy()

# 创建迁移对象
migrate = None

# 创建redis连接对象
redis_store = None

# 配置日志信息
# 创建日志记录器,指明日志保存的路径,每个日志文件的最大大小,保存日志文件个数上限
file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100,
                                       backupCount=10)
# 创建日志记录的格式:日志等级 报错文件名 行号 日志信息
formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(filename)s:%(lineno)d %(message)s')
# 将上述格式设置进日志记录器
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象(flask.app使用的)添加日志记录器
logging.getLogger().addHandler(file_log_handler)
# 设置日志记录等级
logging.basicConfig(level=logging.DEBUG)


# 创建应用工厂方法
def create_app(config_name):
    # 创建app对象
    app = Flask(__name__)
    # 添加配置类
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)
    # 设置session存储到redis中
    Session(app)
    # 为flask补充csrf防护
    # CSRFProtect(app)
    # 将数据库对象初始化app
    db.init_app(app)
    # 修改数据迁移对象
    global migrate
    migrate = Migrate(app, db)
    # 修改redis连接对象
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST,
                              port=config_class.REDIS_PORT,
                              db=1,
                              decode_responses=True)
    # 注册自定义转换器
    from .utils.commons import ReConverter
    app.url_map.converters['re'] = ReConverter

    # 注册蓝图
    from .api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/v1.0/')
    # 注册静态文件蓝图
    from .web_html import web_html
    app.register_blueprint(web_html, url_prefix='/')

    return app


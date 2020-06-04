import redis


class Config(object):
    """配置信息类"""
    # 密钥
    SECRET_KEY = 'anjdaw1823u9812ndajn23'

    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@127.0.0.1:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # flask-session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    SESSION_USE_SIGNER = True  # 对cookie中的session_id进行签名处理
    # session有效期,单位秒
    PERMANENT_SESSION_LIFETIME = 86400


class DevelopConfig(Config):
    # 调试模式
    DEBUG = True


class ProductConfig(Config):
    pass


config_map = {
    'dev': DevelopConfig,
    'prod': ProductConfig
}

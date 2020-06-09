from flask import Blueprint

# 创建蓝图对象
api = Blueprint('api', __name__)

# 导入蓝图的视图,使app能够接管视图
from . import verify_code, passport

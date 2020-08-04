from ihome.api_1_0 import api
from flask import request, jsonify, current_app, session
from ihome import redis_store, db
from ihome.models import User
from ihome.utils.response_code import RET
from sqlalchemy.exc import IntegrityError
import re


@api.route('users/', methods=['POST'])
def register():
    # 获取数据
    req_data = request.get_json()
    mobile = req_data.get('mobile')
    sms_code = req_data.get('phonecode')
    password = req_data.get('password')
    password2 = req_data.get('password2')

    # 校验数据
    # 完整性
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 手机号
    if not re.match(r'1[3|5|7|8]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')

    # 两次密码是否一致
    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg='输入的两次密码不一致')

    # 短信验证码
    try:
        real_sms_code = redis_store.get('sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='获取真实短信验证码失败')
    # 若redis中数据不存在,返回的值为None,而不会抛异常
    if not real_sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg='短信验证码不存在或已过期')
    # 判断验证码
    if sms_code != real_sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg='短信验证码错误')
    # 删除验证码
    try:
        redis_store.delete('sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
    # 加密密码
    # 方法一.直接将密码加密
    #  password_hash = generate_password_hash(password)
    #  user = User(name=mobile, password_hash=password_hash, mobile=mobile)

    # 方法二.将加密步骤放入模型类中,通过property设置
    # 创建用户
    user = User(name=mobile, mobile=mobile)
    # 设置加密密码
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='该手机号已注册')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    # 设置登录session
    session['user_id'] = user.id
    session['name'] = user.mobile
    session['mobile'] = user.mobile

    return jsonify(errno=RET.OK, errmsg='成功')


@api.route('sessions/', methods=['POST'])
def login():
    # 获取数据
    req_data = request.get_json()
    mobile = req_data.get('mobile')
    password = req_data.get('password')

    # 校验数据
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    # 获取登录手机号的数据库信息
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')
    if not user:
        return jsonify(errno=RET.PARAMERR, errmsg='该手机号用户不存在')
    if not user.check_password(password):
        return jsonify(errno=RET.PARAMERR, errmsg='密码错误')

    return jsonify(errno=RET.OK, errmsg='成功')

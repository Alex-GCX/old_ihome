from ihome.utils.captcha.captcha import captcha
from . import api
from ihome import redis_store, constants
from flask import current_app, jsonify, make_response, request
from ihome.utils.response_code import RET
from ihome.libs.yuntongxun.sms import CCP
from ihome.tasks.task_sms import send_sms
import random
from datetime import datetime


@api.route('image_codes/<image_code_id>/')
def get_image_code(image_code_id):
    """获取图片验证码"""
    # 接收前端传过来的id,与将要生成的验证码一一对应存入redis
    # 名字,真实文本,图片数据
    name, text, image_data = captcha.generate_captcha()
    # 存入redis中
    try:
        redis_store.setex('image_code_%s' %
                          image_code_id,constants.REDIS_IMAGE_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败')
    resp = make_response(image_data)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


@api.route("smscodes/<re(r'1[3|5|7|8]\d{9}'):mobile>/")
def get_smscode(mobile):
    # 校验传过来的图片验证码是否正确
    image_code_id = request.args.get('image_code_id')
    image_code = request.args.get('image_code')
    if not all([image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 获取redis中真实的验证码
    try:
        real_code = redis_store.get('image_code_%s' %
                                    image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取图片验证码失败')
    # 判断真实验证码是否过期
    if not real_code:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已过期')
    # 比较用户验证码与真实验证码
    if image_code.lower() != real_code.lower():
        return jsonify(errno=RET.PARAMERR, errmsg='图片验证码错误')
    # 删除redis中取出的验证码,防止用户使用同一个图片验证码验证多次
    try:
        redis_store.delete('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 判断60秒内该手机号是否发送过验证码
    try:
        send_flag = redis_store.get('has_send_sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(errno=RET.DATAEXIST,
                                 errmsg='获取手机发送历史记录错误')
    else:
        if send_flag:
            return jsonify(errno=RET.REQERR,
                           errmsg='手机发送短信过于频繁,请60s后再试')

    # 获取手机验证码
    sms_code = '%06d' % random.randint(0, 999999)
    # 保存手机验证码
    redis_store.setex('sms_code_%s' % mobile, constants.REDIS_SMS_CODE_EXPIRES,
                      sms_code)
    # 同步发送短信
    #  try:
        #  ccp = CCP()
        #  result = ccp.send_template_sms(mobile, [sms_code,
                                                #  int(constants.REDIS_SMS_CODE_EXPIRES/60)],
                                      #  1)
    #  except Exception as e:
        #  current_app.logger.error(e)
        #  return jsonify(errno=RET.THIRDERR, errmsg='发送短信异常')
#
    #  # 返回
    #  if result == 0:
        #  # 记录该手机发送成功,60秒不能再发送
        #  try:
            #  redis_store.setex('has_send_sms_code_%s' % mobile,
                              #  constants.REDIS_SMS_CODE_SEND_EXPIRES,
                              #  1)
        #  except Exception as e:
            #  current_app.llogger.error(e)
        #  return jsonify(errno=RET.OK, errmsg='发送成功')
    #  else:
        #  return jsonify(errno=RET.THIRDERR, errmsg='发送失败')

    # 异步发送短信
    result = send_sms(mobile, [sms_code, int(constants.REDIS_SMS_CODE_SEND_EXPIRES/60)],
            1)
    return jsonify(errno=RET.OK, errmsg='发送成功')

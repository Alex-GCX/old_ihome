from ihome.utils.captcha.captcha import captcha
from . import api
from ihome import redis_store, constants
from flask import current_app, jsonify, make_response
from ihome.utils.response_code import RET

@api.route('image_codes/<image_code_id>')
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

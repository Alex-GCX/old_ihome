from ihome.tasks.main import celery_app
from ihome.libs.yuntongxun.sms import CCP
from ihome import constants
from ihome import redis_store
from flask import current_app
import time

@celery_app.task
def send_sms(to, data, template):
    ccp = CCP()
    time.sleep(3)
    result = ccp.send_template_sms(to, data, template)
    if result == 0:
        # 记录该手机发送成功,60秒不能再发送
        try:
            redis_store.setex('has_send_sms_code_%s' % to,
                              constants.REDIS_SMS_CODE_SEND_EXPIRES,
                              1)
        except Exception as e:
            current_app.logger.error(e)
            return 1
        return 0
    else:
        return 1

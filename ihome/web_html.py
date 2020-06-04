from flask import Blueprint, make_response, current_app
from flask_wtf import csrf

web_html = Blueprint('web_html', __name__)

@web_html.route("/<re('.*'):html_name>")
def get_html(html_name):
    if not html_name:
        # :5000/
        file_name = 'index.html'

    # 如果资源名不是favicon.ico
    if html_name != 'favicon.ico':
        file_name = 'html/' + html_name

    # 创建一个csrf_token的值
    csrf_token = csrf.generate_csrf()

    # flask提供的返回静态文件的方法
    resp = make_response(current_app.send_static_file(file_name))

    # 设置csrf_token的cookie
    resp.set_cookie('csrf_token', csrf_token)
    return resp

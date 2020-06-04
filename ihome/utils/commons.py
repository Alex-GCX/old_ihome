from werkzeug.routing import BaseConverter

class ReConverter(BaseConverter):
    """自定义正则转换器"""
    def __init__(self, url_map, regex):
        # 继承父类方法
        super().__init__(url_map)
        self.regex = regex

model_header_template = """
from pydantic import BaseModel
from typing import *


"""

model_template = """
class {{ class_name }}(BaseModel):
    {% if args %}{% for arg_name, arg_type_limit in args %}{{ arg_name }}: {{ arg_type_limit }}
    {% endfor %}{% else %}
    ...
    {% endif %}"""

env_template = """
from models import {{ env_name.upper() }}_ENV_ARGS

class {{ env_name.upper() }}_ENV:
    def __init__(self, args: dict = {}):
        \"\"\"
        初始化环境
        Args:
            args: 环境参数构成的字典

        \"\"\"
        self.env_name = "{{ env_name }}"

        # 校验环境参数，不需要校验可以注释下面一行
        args = check_model(args, {{ env_name.upper() }}_ENV_ARGS)
        
        {% if args %}{% for arg in args %}self.{{ arg }} = args.get("{{ arg }}")
        {% endfor %}{% endif %}
        self.build()

    def build(self):
        \"\"\"
        环境构建
        可根据环境参数提前构建部分数据
        例如登录、获取token等
        \"\"\"
        ...
"""

init_template = """
{% for func_id, class_name in init_list %}
from .{{ func_id }} import {{ class_name }}
{% endfor %}
"""


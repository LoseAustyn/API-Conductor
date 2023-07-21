model_header = """
from pydantic import BaseModel
from typing import *


"""

model_template = """
class {{ class_name }}(BaseModel):
    {% if args %}{% for arg_name, arg_type_limit in args %}{{ arg_name }}: {{ arg_type_limit }}
    {% endfor %}{% else %}
    ...
    {% endif %}"""



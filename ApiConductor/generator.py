from tools import *
import yaml
import traceback
import shutil
from typing import Any
import jinja2

_types_dict = {
    "string": "str",
    "bytes": "str",
    "boolean": "bool",
    "float": "float",
    "object": "dict",
    "integer": "int",
    "any": "Any"
}


def generate(file_path: str):
    """
    生成插件
    Args:
        file_path: yaml文件目录

    """
    Log.info("正在使用API Conductor生成插件")

    #   读取插件定义文件
    plugin_data = read_generate_file(file_path)

    #   生成基础文件
    generate_base_file()

    #   生成自定义类
    types_model = generate_types_model()


def read_generate_file(file_path: str) -> dict:
    """
    读取插件定义文件
    Args:
        file_path:  yaml文件目录

    Returns:
        plugin_data: 转换成dict形式的插件数据

    """

    #   获取插件定义文件的绝对路径
    if not os.path.isabs(file_path):
        os.path.join(os.getcwd(), file_path)

    Log.info("读取插件定义文件中")

    #   简单的路径检测
    path_check(file_path)

    try:
        file_bytes = open(file_path, "rb").read()

        if b"\r" in file_bytes:
            Log.warning(r"检测到插件定义文件中存在'\r'换行符" + "\n请尽量使用LF换行格式，以防不可知的错误")

        plugin_data = yaml.load(file_bytes.decode("utf-8"), Loader=yaml.FullLoader)

    except UnicodeDecodeError:
        raise Exception("编码格式错误，请将yaml文件转成utf-8编码格式")

    except Exception as error:
        raise Exception(f"yaml文件打开失败，错误未知：\n{error}\nTraceback:\n{traceback.format_exc()}")

    #   插件必要元数据检测
    data_check(plugin_data)

    Log.info(f"插件定义文件读取完成")

    return plugin_data


def path_check(file_path: str):
    """
    插件路径检测
    Args:
        file_path:  yaml文件目录

    """
    #   路径检测
    if not os.path.exists(file_path):
        raise Exception(f"文件路径错误，请检查路径是否正确：{file_path}")

    #   类型检测
    if any(file_path.endswith(end) for end in ["yml", "yaml"]):
        pass
    else:
        raise Exception(f"文件类型错误，请检查是否为yaml文件：{file_path}")


def data_check(data: dict):
    """
    插件元数据验证
    Args:
        data: 插件定义数据

    """
    Log.debug("校验插件元数据中")

    error = ""

    check_keys = [
        "id",
        "title",
        "version",
        "author"
    ]

    for key in check_keys:
        if not data.get(key):
            error += f"{key}\n"

        if error:
            raise Exception(f"插件定义文件中缺失必要参数：\n {error}")

    if not data["id"].islower():
        raise Exception(f"插件ID应该为全小写：{data['id']}")

    if not (data["id"][0].isalnum() and data["id"][0].isalpha()):
        raise Exception(f"插件ID应该以小写字母开头：{data['id']}")

    if not (data["id"].replace("_", "").isalnum()):
        raise Exception(f"插件ID只允许使用字母，数字和下划线")

    Log.debug("插件元数据校验通过")


def generate_base_file():
    """
    生成插件的基础文件

    """
    Log.info("生成基础文件中")

    resource_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "res")

    resource_files = os.listdir(resource_dir)

    if "__pycache__" in resource_files:
        resource_files.remove("__pycache__")

    resource_files.remove("plugin.yaml")

    for file_name in resource_files:
        try:
            #   基础文件位置
            resource_file_path = os.path.join(resource_dir, file_name)
            #   生成位置
            file_path = os.path.join(os.getcwd(), file_name)

            #   若文件存在则跳过生成
            if os.path.exists(file_path):
                Log.attention(f"{file_name} 已存在，跳过生成")

            elif os.path.isdir(resource_file_path):
                shutil.copytree(resource_file_path, file_path)
            else:
                shutil.copy2(resource_file_path, file_path)

            Log.info(f"{file_name} 生成完成")

        except Exception as error:
            raise Exception(f"{file_name} 生成失败，错误未知：\n{error}\nTraceback:\n{traceback.format_exc()}")

    Log.info("基础文件生成完成")


def generate_types_model(types: list) -> str:
    """
    根据插件定义文件中types参数生成自定义类型的校验模型
    Args:
        types: 自定义类型列表

    Returns:
        types_model: 自定义类型的校验模型，需要在models.py文件中写入

    """

    #   所有自定义类型的校验内容
    types_model = ""

    if not types:
        Log.attention("未检测到自定义类型，跳过自定义类型校验数据的生成")
        return types_model

    for type_ in types:
        Log.info(f"生成 {type_['id']} 类型校验数据中")

        _types_dict[type_] = type_.upper()

        type_data = {
            #   类名采用全大写
            "class_name": type_["id"].upper(),
            #   对类的构成参数进行打包
            "args": args_setup(type_["args"])
        }

        types_model += render_string(type_data)


def args_setup(args: list) -> list:
    """
    将参数格式化用于生成models
    Args:
        args: 参数列表

    Returns:
        args_list: 格式化后参数列表

    """
    args_list = []

    if not args:
        Log.attention(f"参数列表为空，已跳过校验数据生成")
        return args_list

    #   提取一个参数的属性
    for arg in args:
        #   从参数中获取关键信息
        arg_id = arg["id"]
        arg_type = arg.get("type")
        arg_required = arg.get("required", False)
        arg_default = arg.get("default")
        arg_enum = arg.get("enum")

        #   校验参数的属性是否符合规范
        arg_check(arg_id, arg_type, arg_default, arg_enum)

        args_list.append([
            arg_id,
            type_transform(arg_type, arg_required, arg_default, arg_enum)
        ])

    return args_list


def arg_check(arg_id: str, arg_type: str, arg_default: Any, arg_enum: list):
    """
    校验参数的属性是否符合规范
    Args:
        arg_id: 参数id
        arg_type: 参数类型
        arg_default: 参数默认值
        arg_enum: 参数枚举值

    """

    Log.debug(f"校验{arg_id}的属性中")

    if not arg_type and not arg_enum:
        raise Exception(f"类型与枚举集合都为空\n类型（type）与枚举集合（enum）请至少填写一项")

    if arg_type and not _types_dict.get(arg_type):
        if arg_type.startswith("[]") and not _types_dict.get(arg_type[2:]):
            raise Exception(f"未知类型的列表组合：{arg_type}，如果存在自定义类型嵌套，请注意顺序")
        elif not arg_type.startswith("[]") and not _types_dict.get(arg_type):
            raise Exception(f"未知的类型：{arg_type}，如果存在自定义类型嵌套，请注意顺序")

    if arg_enum and not isinstance(arg_enum, list):
        raise Exception("枚举集合（enum）填写不符合规范")

    if arg_default and arg_enum and arg_default not in arg_enum:
        raise Exception(f"默认值 {arg_default}\n无法在枚举的集合中找到")

    if not arg_enum:
        raise Exception("枚举集合为空")

    Log.debug(f"{arg_id}的属性校验通过")


def type_transform(arg_type: str, arg_required: bool, arg_default: Any, arg_enum: list):
    """

    Args:
        arg_type: 参数类型
        arg_required: 参数是否必填
        arg_default: 参数默认值
        arg_enum: 参数枚举值

    Returns:
        arg_type_limit: 参数的验证typing信息

    """

    arg_type_limit = ""

    #   存在枚举值时，限制输入参数只能从枚举的值中选择
    if arg_enum:
        arg_type_limit = f"Literal{arg_enum}"

    elif arg_type.startswith("[]"):
        arg_type_limit = f"Optional[List[{_types_dict.get(arg_type)}]]"

    else:
        arg_type_limit = _types_dict.get(arg_type)

    if not arg_required and arg_default is None:
        arg_type_limit += " = None"

    elif arg_default is not None:
        if type(arg_default) == str:
            arg_type_limit += f" = \"{arg_default}\""
        else:
            arg_type_limit += f" = {arg_default}"

    return arg_type_limit


def render_string(data: dict, template: str):
    """
    通过jinja2库渲染字符串
    Args:
        data: 渲染用的数据
        template: 渲染的模板

    Returns:
        rendered_string: 渲染完成的字符串

    """

    template = jinja2.Template(template)
    rendered_string = template.render(data)

    return rendered_string

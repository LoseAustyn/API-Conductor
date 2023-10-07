import os

from .tools import *
import yaml
import traceback
import shutil
from typing import Any
import jinja2
from .templates import *

#   预设类型
_types_dict_ = {
    "string": "str",
    "bytes": "str",
    "boolean": "bool",
    "float": "float",
    "map": "dict",
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
    types_data = plugin_data.get("types")
    envs_data = plugin_data.get("envs")
    apis_data = plugin_data.get("apis")

    #   生成基础文件
    generate_base_file()

    #   生成环境初始化文件
    generate_envs_init_files(envs_data)

    #   生成接口初始化文件
    generate_apis_init_files(apis_data)

    #   生成自定义类校验数据
    types_model = generate_types_model(types_data)

    #   生成环境校验数据
    env_model = generate_envs_model(envs_data)

    #   生成接口校验数据
    api_model = generate_apis_model(apis_data)

    #   生成校验文件
    generate_envs_models_files(types_model, env_model)
    generate_apis_models_files(types_model, api_model)

    #   生成代码文件
    generate_envs_files(envs_data)
    generate_apis_files(apis_data)

    #   生成启动文件
    generate_main_file()


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


def generate_envs_init_files(envs: dict):
    """

    生成初始化文件

    Args:

        envs: 环境

    """

    work_path = os.getcwd()

    if envs and type(envs) == dict:

        Log.info("生成环境初始化文件中")

        envs_path = os.path.join(work_path, "envs")
        if not os.path.exists(envs_path):
            os.mkdir(envs_path)

        envs_data = {
            "init_list": [(env, env.upper() + "_ENV") for env in envs.keys()]
        }
        init_file = render_string(envs_data, init_template)

        with open(os.path.join(envs_path, "__init__.py"), "w", newline="\n", encoding="utf-8") as file:
            file.write(init_file)

    else:

        Log.info("未检测到有环境数据，跳过环境初始化文件生成")


def generate_apis_init_files(apis: dict):
    """

    生成APIs初始化文件

    Args:
        apis: 接口

    """

    work_path = os.getcwd()

    if apis and type(apis) == dict:

        Log.info("生成接口初始化文件")

        apis_path = os.path.join(work_path, "apis")
        if not os.path.exists(apis_path):
            os.mkdir(apis_path)

        apis_list = {
            "init_list": [(api, api.upper() + "_API") for api in apis.keys()]
        }
        init_file = render_string(apis_list, init_template)

        with open(os.path.join(apis_path, "__init__.py"), "w", newline="\n", encoding="utf-8") as file:
            file.write(init_file)

    else:

        Log.info("未检测到有接口数据，跳过接口初始化文件生成")


def generate_types_model(types: dict) -> str:
    """

    根据插件定义文件中types参数生成自定义类的校验模型

    Args:
        types: 自定义类型字典

    Returns:
        types_model: 自定义类型的校验模型，需要在models.py文件中写入

    """

    #   所有自定义类型的校验内容
    types_model = ""

    if not types:
        Log.attention("未检测到自定义类型，跳过自定义类型校验数据的生成")
        return types_model

    for type_ in types.keys():
        Log.info(f"生成 {type_} 类型校验数据中")

        _types_dict_[type_] = type_.upper()

        type_data = {
            #   类名采用全大写
            "class_name": type_.upper(),
            #   对类的构成参数进行打包
            "args": args_setup(types[type_]["args"])
        }

        types_model += render_string(type_data, model_template)

        Log.info(f"{type_} 类型校验数据生成完成")

    Log.info("自定义类型（types）校验数据生成完成")

    return types_model


def generate_envs_model(envs: dict) -> str:
    """

    根据插件定义文件中envs参数生成环境变量的校验模型

    Args:
        envs: 环境

    Returns:
        envs_model: 环境变量的校验模型，需要在models.py文件中写入

    """

    envs_model = ""

    if not envs:
        Log.attention("未检测到环境配置，跳过环境校验数据的生成")
        return envs_model

    for env in envs.keys():
        Log.info(f"生成 {env} 环境校验数据中")

        env_data = {
            #   类名采用全大写
            "class_name": env.upper() + "_ENV_ARGS",
            #   对构成参数进行打包
            "args": args_setup(envs[env]["args"])
        }

        envs_model += render_string(env_data, model_template)

        Log.info(f"{env} 环境校验数据生成完成")

    Log.info("环境（envs）校验数据生成完成")

    return envs_model


def generate_apis_model(apis: dict) -> str:
    """

    根据插件定义文件中apis生成入参和出参的校验模型

    Args:
        apis: 接口

    Returns:
        apis_model: 接口的校验模型，需要在models.py文件中写入
    """

    apis_model = ""

    if not apis:
        Log.attention("未检测到接口配置，跳过接口校验数据的生成")
        return apis_model

    for api in apis.keys():
        Log.info("生成接口（api）校验数据中")

        #   输入参数
        api_input_data = {
            "class_name": api.upper() + "_API_INPUT",
            "args": args_setup(apis[api]["input"]),
        }

        #   输出参数
        api_output_data = {
            "class_name": api.upper() + "_API_OUTPUT",
            "args": args_setup(apis[api]["output"]),
        }

        apis_model = render_string(api_input_data, model_template) + \
                     render_string(api_output_data, model_template)

    Log.info("接口（apis）校验数据生成完成")

    return apis_model


def generate_envs_models_files(types_model: str, env_model: str):
    """

    生成校验文件

    Args:
        types_model: 自定义类校验数据
        env_model: 环境校验数据

    """

    work_path = os.getcwd()

    if env_model:
        Log.info("生成环境校验文件中")

        envs_path = os.path.join(work_path, "envs", "models.py")
        with open(envs_path, "w", encoding="utf-8", newline="\n") as file:
            file.write(model_header_template + types_model + env_model)

        Log.info("环境校验文件生成完成")

    else:
        Log.info("不存在环境数据，已跳过环境校验文件生成")


def generate_apis_models_files(types_model: str, api_model: str):
    """

    生成校验文件

    Args:
        types_model: 自定义类校验数据
        api_model: 环境校验数据

    """

    work_path = os.getcwd()

    if api_model:
        Log.info("生成接口校验文件中")

        apis_path = os.path.join(work_path, "apis", "models.py")
        with open(apis_path, "w", encoding="utf-8", newline="\n") as file:
            file.write(model_header_template + types_model + api_model)

        Log.info("接口校验文件生成完成")

    else:
        Log.info("不存在接口数据，已跳过接口校验文件生成")


def generate_envs_files(envs_data: dict):
    """

    生成环境py文件

    Args:
        envs_data: 环境数据

    """

    work_path = os.getcwd()

    if envs_data:
        Log.info("生成环境文件中")

        for env_name, env_meta in envs_data.items():
            env_data = {
                "env_name": env_name,
                "args": env_meta["args"].keys() if type(env_meta.get("args")) is dict else []
            }

            env_file = render_string(env_data, env_template)

            env_path = os.path.join(work_path, "envs", f"{env_name}.py")

            with open(env_path, "w", newline="\n", encoding="utf-8") as file:
                file.write(env_file)

            Log.info(f"{env_name}.py 生成完成")

    else:
        Log.info("不存在环境数据，已跳过环境文件生成")


def generate_apis_files(apis_data: dict):
    """

    生成接口py文件

    Args:
        apis_data: 接口数据

    """

    work_path = os.getcwd()

    if apis_data:
        Log.info("生成接口文件中")

        for api_name, api_meta in apis_data.items():
            api_data = {
                "api_name": api_name,
                "input": api_meta["input"].keys() if type(api_meta.get("input")) is dict else []
            }

            api_file = render_string(api_data, api_template)

            api_path = os.path.join(work_path, "apis", f"{api_name}.py")

            with open(api_path, "w", newline="\n", encoding="utf-8") as file:
                file.write(api_file)

            Log.info(f"{api_name}.py 生成完成")

    else:
        Log.info("不存在接口数据，已跳过接口文件生成")


def generate_main_file():
    """

    生成启动文件

    """

    work_path = os.getcwd()

    Log.info("生成启动文件中")

    main_path = os.path.join(work_path, "main.py")

    with open(main_path, "w", encoding="uft-8", newline="\n") as file:
        file.write(main_template)

    Log.info("生成启动文件完成")


def args_setup(args: dict) -> list:
    """

    将参数格式化用于生成models

    Args:
        args: 参数字典

    Returns:
        args_list: 格式化后参数列表

    """
    args_list = []

    if not args:
        Log.attention(f"参数列表为空，已跳过校验数据生成")
        return args_list

    #   提取一个参数的属性
    for arg_id, arg_property in args.items():
        #   从参数中获取关键信息
        arg_type = arg_property.get("type")
        arg_required = arg_property.get("required", False)
        arg_default = arg_property.get("default")
        arg_enum = arg_property.get("enum")

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

    if arg_type and not _types_dict_.get(arg_type):
        if arg_type.startswith("[]") and not _types_dict_.get(arg_type[2:]):
            raise Exception(f"未知类型的列表组合：{arg_type}，如果存在自定义类型嵌套，请注意顺序")
        elif not arg_type.startswith("[]") and not _types_dict_.get(arg_type):
            raise Exception(f"未知的类型：{arg_type}，如果存在自定义类型嵌套，请注意顺序")

    if arg_enum and not isinstance(arg_enum, list):
        raise Exception("枚举集合（enum）填写不符合规范")

    if arg_default and arg_enum and arg_default not in arg_enum:
        raise Exception(f"默认值 {arg_default}\n无法在枚举的集合中找到")

    if arg_enum is []:
        raise Exception("枚举集合为空")

    Log.debug(f"{arg_id}的属性校验通过")


def type_transform(arg_type: str, arg_required: bool, arg_default: Any, arg_enum: list) -> str:
    """

    根据yaml中填入的类型生成models中的类型验证

    Args:
        arg_type: 参数类型
        arg_required: 参数是否必填
        arg_default: 参数默认值
        arg_enum: 参数枚举值

    Returns:
        arg_type_limit: 参数的验证typing信息

    """

    #   存在枚举值时，限制输入参数只能从枚举的值中选择
    if arg_enum:
        arg_type_limit = f"Literal{arg_enum}"

    elif arg_type.startswith("[]"):
        arg_type_limit = f"Optional[List[{_types_dict_.get(arg_type)}]]"

    else:
        arg_type_limit = _types_dict_.get(arg_type)

    if not arg_required and arg_default is None:
        arg_type_limit += " = None"

    elif arg_default is not None:
        if type(arg_default) == str:
            arg_type_limit += f" = \"{arg_default}\""
        else:
            arg_type_limit += f" = {arg_default}"

    return arg_type_limit


def render_string(data: dict, template: str) -> str:
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

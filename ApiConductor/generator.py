from tools import *
import yaml
import traceback
import shutil


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
        types: 自定义类型

    Returns:
        types_model: 自定义类型的校验模型，需要在models.py文件中写入

    """

    if not types:
        Log.attention("未检测到自定义类型，跳过自定义类型校验数据的生成")
        return ""




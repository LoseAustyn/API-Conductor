import argparse
from .generator import generate
from .tools import Log

version = "0.0.1"


def cmdline():
    """

    创建命令行解析对象

    """

    #   初始化日志系统
    Log()

    description = f"""
#   -h, --help              查看帮助信息
#   -v, --version           查看版本
#   -g, --generate          生成插件
"""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description
    )

    #   添加命令
    parser.add_argument(
        "-v",
        "--version",
        help="查看版本",
        action='version',
        version=f"API Conductor: {version}"
    )
    parser.add_argument(
        "-g",
        "--generate",
        help="生成插件",
        action="append"
    )
    parser.add_argument(
        "-hp",
        "--http",
        help="启动api接口",
        action="store_true"
    )

    #   获取add_argument中action的参数
    args = parser.parse_args()

    if args.generate:
        file_path = args.generate[0]
        generate(file_path)

    elif args.http:
        ...

    else:
        pass


if __name__ == "__main__":
    cmdline()

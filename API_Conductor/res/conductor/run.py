import sys
from API_Conductor.res.conductor.tools import Log
from api import run_server


def run():
    """
    启动插件
    """
    Log.info("启动插件")

    try:
        host = str(sys.argv[0])
    except:
        host = "0.0.0.0"

    try:
        port = int(sys.argv[1])
    except:
        port = 18024

    run_server(host, port)

    
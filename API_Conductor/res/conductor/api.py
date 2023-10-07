import uvicorn
from fastapi import FastAPI
from API_Conductor.res.conductor.tools import Log
from models import *

_api_server_ = FastAPI(title="API Conductor")


@_api_server_.post("/apis/{apis_name}", tags=["接口"])
async def apis(apis_name: str, data: APIS_DATA):
    """

    最直接的启动方式

    Args:
        apis_name: 接口名称
        data: 启动数据

    """





def run_server(host: str = "0.0.0.0", port: int = 18024):
    """

    启动Conductor的API服务

    Args:
        host: 地址
        port: 端口

    """
    Log.attention(f"如果有需要，在浏览器输入 http://{host}:{port}/docs 以进行接口测试")
    uvicorn.run("conductor:_api_server_", host=host, port=port, reload=True)

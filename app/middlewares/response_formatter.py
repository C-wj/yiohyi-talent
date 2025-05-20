"""
响应格式化中间件
用于统一处理API响应格式，确保所有响应符合标准格式：{code: 0, data: object, msg: ''}
"""
from typing import Any, Callable, Dict
import json

from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.response import standard_response


class ResponseFormatterMiddleware:
    """
    响应格式化中间件
    将所有API响应转换为标准格式 {code: 0, data: object, msg: ''}
    """
    
    def __init__(self, app: ASGIApp):
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """处理每个请求并格式化响应"""
        # 只处理HTTP请求
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 创建响应拦截
        async def _send(message: Dict[str, Any]):
            # 仅处理响应类型的消息
            if message["type"] == "http.response.start":
                # 获取原始响应头部信息
                headers = [(key, value) for key, value in message.get("headers", [])]
                content_type = None
                
                # 查找Content-Type头
                for key, value in headers:
                    if key.decode("utf-8").lower() == "content-type":
                        content_type = value.decode("utf-8").lower()
                        break
                
                # 只处理JSON响应
                if content_type and "application/json" in content_type:
                    # 保存原始状态码
                    original_status = message["status"]
                    
                    # 如果状态码不是2xx，将在body处理时将其转换为相应的错误码
                    self.original_status = original_status
                
                # 传递消息
                await send(message)
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                more_body = message.get("more_body", False)
                
                # 如果有响应体且是JSON格式，尝试格式化
                if body and hasattr(self, "original_status"):
                    try:
                        # 解析原始响应体
                        data = json.loads(body.decode("utf-8"))
                        
                        # 检查是否已经符合标准格式
                        if isinstance(data, dict) and "code" in data and "data" in data and "msg" in data:
                            # 已经符合标准格式，不做处理
                            pass
                        else:
                            # 根据状态码确定code值
                            if 200 <= self.original_status < 300:
                                # 成功响应
                                formatted_data = standard_response(data=data)
                            else:
                                # 错误响应
                                error_code = self.original_status
                                error_msg = "请求失败"
                                
                                # 如果原始响应中包含错误信息，使用它
                                if isinstance(data, dict) and "detail" in data:
                                    error_msg = data["detail"]
                                
                                formatted_data = standard_response(
                                    data=None, 
                                    code=error_code,
                                    msg=error_msg
                                )
                            
                            # 替换响应体
                            body = json.dumps(formatted_data).encode("utf-8")
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # 如果不是有效的JSON或无法解码，不做处理
                        pass
                
                # 发送处理后的响应体
                await send({
                    "type": "http.response.body",
                    "body": body,
                    "more_body": more_body
                })
            else:
                # 其他类型的消息直接传递
                await send(message)
        
        # 使用拦截的send函数
        await self.app(scope, receive, _send) 
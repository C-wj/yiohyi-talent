"""
标准API响应处理模块
根据@api.mdc规范，返回统一格式的响应
"""
from typing import Any, Dict, List, Optional, Union
import json
from datetime import datetime, date

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """标准API响应模型"""
    code: int = 0
    data: Optional[Any] = None
    msg: str = ""

    class Config:
        arbitrary_types_allowed = True


# 自定义JSON编码器，处理datetime等特殊类型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def standard_response(
    data: Any = None,
    code: int = 0,
    msg: str = "success"
) -> Dict[str, Any]:
    """
    创建标准API响应
    遵循 {code: 0, data: object, msg: ''} 格式
    
    Args:
        data: 响应数据
        code: 状态码，0表示成功，其他值表示错误
        msg: 消息说明
    
    Returns:
        Dict: 标准格式的API响应
    """
    return {
        "code": code,
        "data": data,
        "msg": msg
    }


def success_response(data: Any = None, msg: str = "success") -> Dict[str, Any]:
    """
    成功响应
    
    Args:
        data: 响应数据
        msg: 响应消息
        
    Returns:
        Dict[str, Any]: 标准格式的成功响应
    """
    return {
        "code": 0,
        "data": data,
        "msg": msg
    }


def error_response(msg: str, code: int = 500, data: Any = None) -> Dict[str, Any]:
    """
    错误响应
    
    Args:
        msg: 错误消息
        code: 错误码，默认为500
        data: 错误相关数据
        
    Returns:
        Dict[str, Any]: 标准格式的错误响应
    """
    return {
        "code": code,
        "data": data,
        "msg": msg
    }


def unauthorized_response(msg: str = "请先登录") -> Dict[str, Any]:
    """
    未授权响应
    
    Args:
        msg: 错误消息
        
    Returns:
        Dict[str, Any]: 标准格式的未授权响应
    """
    return error_response(msg, code=401)


def validation_error_response(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    创建验证错误响应
    
    Args:
        errors: 验证错误列表
    
    Returns:
        Dict: 验证错误响应
    """
    return error_response(
        msg="请求参数验证失败",
        code=400,
        data={"errors": errors}
    )


def not_found_response(msg: str = "资源不存在") -> Dict[str, Any]:
    """
    创建资源未找到响应
    
    Args:
        msg: 未找到消息
    
    Returns:
        Dict: 资源未找到响应
    """
    return error_response(msg=msg, code=404)


class ApiJSONResponse(JSONResponse):
    """标准API JSON响应类"""
    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        code: int = 0,
        msg: str = "success",
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[Any] = None,
    ) -> None:
        """
        初始化API JSON响应
        
        Args:
            content: 原始内容
            status_code: HTTP状态码
            code: API状态码
            msg: 消息
            headers: HTTP头
            media_type: 媒体类型
            background: 后台任务
        """
        # 如果content已经是标准响应格式，则直接使用
        if isinstance(content, dict) and all(key in content for key in ["code", "data", "msg"]):
            standardized_content = content
        else:
            # 否则转换为标准响应格式
            standardized_content = {
                "code": code,
                "data": content,
                "msg": msg
            }

        # 使用自定义JSON编码器
        self.json_encoder = CustomJSONEncoder
            
        super().__init__(
            content=standardized_content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        ) 
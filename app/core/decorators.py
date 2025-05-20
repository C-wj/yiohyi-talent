"""
装饰器模块
包含API响应处理等功能
"""
import functools
import inspect
from typing import Any, Callable, Dict, TypeVar, cast

from fastapi import Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.response import ApiJSONResponse

# 泛型类型
F = TypeVar("F", bound=Callable[..., Any])


def api_response(func: F) -> F:
    """
    API响应装饰器，确保所有API返回标准格式 {code: 0, data: object, msg: ''}
    
    Args:
        func: 原始API处理函数
        
    Returns:
        装饰后的函数
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)
        
        # 如果已经是Response对象，则直接返回
        if isinstance(result, Response):
            return result
        
        # 如果已经是标准格式，则直接转换为JSONResponse返回
        if isinstance(result, dict) and all(key in result for key in ["code", "data", "msg"]):
            return JSONResponse(content=result)
        
        # 如果是Pydantic模型，则转换为dict
        if isinstance(result, BaseModel):
            result = result.dict()
        
        # 返回标准格式
        return ApiJSONResponse(content=result)
    
    return cast(F, wrapper) 
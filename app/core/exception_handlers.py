"""
异常处理模块
确保所有API异常也返回标准格式
"""
from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.response import error_response, unauthorized_response


def register_exception_handlers(app: FastAPI) -> None:
    """
    注册异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """处理HTTP异常"""
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            return JSONResponse(
                status_code=status.HTTP_200_OK,  # 统一返回200
                content=unauthorized_response(exc.detail)
            )
        
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            return JSONResponse(
                status_code=status.HTTP_200_OK,  # 统一返回200
                content=error_response(
                    msg=exc.detail,
                    code=404,
                    data=None
                )
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,  # 统一返回200
            content=error_response(
                msg=exc.detail,
                code=exc.status_code,
                data=None
            )
        )
    
    @app.exception_handler(RequestValidationError)
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(
        request: Request, 
        exc: Union[RequestValidationError, ValidationError]
    ) -> JSONResponse:
        """处理验证异常"""
        errors = exc.errors()
        error_details = []
        
        for error in errors:
            error_details.append({
                "loc": error.get("loc", []),
                "msg": error.get("msg", ""),
                "type": error.get("type", "")
            })
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,  # 统一返回200
            content=error_response(
                msg="数据验证错误",
                code=422,
                data=error_details
            )
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """处理所有其他未捕获的异常"""
        return JSONResponse(
            status_code=status.HTTP_200_OK,  # 统一返回200
            content=error_response(
                msg=f"系统错误: {str(exc)}",
                code=500,
                data=None
            )
        ) 
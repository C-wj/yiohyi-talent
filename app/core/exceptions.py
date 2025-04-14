from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class APIError(HTTPException):
    """API错误基类"""
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundError(APIError):
    """404资源未找到错误"""
    def __init__(
        self,
        detail: Any = "资源未找到",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers)


class UnauthorizedError(APIError):
    """401未授权错误"""
    def __init__(
        self,
        detail: Any = "未授权访问",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers)


class ForbiddenError(APIError):
    """403禁止访问错误"""
    def __init__(
        self,
        detail: Any = "禁止访问",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, headers=headers)


class BadRequestError(APIError):
    """400请求错误"""
    def __init__(
        self,
        detail: Any = "请求参数错误",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers)


class ConflictError(APIError):
    """409资源冲突错误"""
    def __init__(
        self,
        detail: Any = "资源冲突",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, headers=headers)


class InternalServerError(APIError):
    """500内部服务器错误"""
    def __init__(
        self,
        detail: Any = "服务器内部错误",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail, headers=headers)


class ServiceUnavailableError(APIError):
    """503服务不可用错误"""
    def __init__(
        self,
        detail: Any = "服务暂时不可用",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail, headers=headers)


class RateLimitExceededError(APIError):
    """429请求过多错误"""
    def __init__(
        self,
        detail: Any = "请求频率过高，请稍后再试",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail, headers=headers)


class ValidationError(BadRequestError):
    """验证错误"""
    def __init__(
        self,
        detail: Any = "数据验证失败",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, headers=headers)


class AuthenticationError(UnauthorizedError):
    """认证错误"""
    def __init__(
        self,
        detail: Any = "身份验证失败",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, headers=headers)


class PermissionDeniedError(ForbiddenError):
    """权限错误"""
    def __init__(
        self,
        detail: Any = "权限不足",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, headers=headers)


class DatabaseError(InternalServerError):
    """数据库错误"""
    def __init__(
        self,
        detail: Any = "数据库操作失败",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, headers=headers)


class FileUploadError(BadRequestError):
    """文件上传错误"""
    def __init__(
        self,
        detail: Any = "文件上传失败",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, headers=headers)


class WechatAPIError(ServiceUnavailableError):
    """微信API错误"""
    def __init__(
        self,
        detail: Any = "微信API调用失败",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, headers=headers) 
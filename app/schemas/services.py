from typing import List, Optional, Dict, Any, Generic, TypeVar

from pydantic import BaseModel, Field

from app.models.user import BaseResponse

# 服务响应模型
class ServiceResponse(BaseResponse):
    """服务响应模型"""
    pass 
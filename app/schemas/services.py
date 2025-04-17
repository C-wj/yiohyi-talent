from typing import Optional, List
from pydantic import BaseModel


class ServiceBase(BaseModel):
    """服务基础模型"""
    id: str
    name: str
    icon: str
    description: str
    url: str
    status: str  # active, coming-soon, disabled


class ServiceResponse(BaseModel):
    """服务响应模型"""
    service: List[ServiceBase]


class ServiceListResponse(BaseModel):
    """服务列表响应模型"""
    code: int
    data: ServiceResponse 
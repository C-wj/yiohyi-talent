from typing import Any, Optional
from bson import ObjectId
from pydantic import BaseModel


class PyObjectId(str):
    """自定义ObjectId类，用于处理MongoDB的ObjectId，兼容pydantic 1.x"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("无效的ObjectId")
        return str(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class StandardResponse(BaseModel):
    """标准响应模型"""
    status: str = "success"
    data: Optional[Any] = None
    message: str = "" 
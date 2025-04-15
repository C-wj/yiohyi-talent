from typing import Any, Optional, Annotated, ClassVar
from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    """自定义ObjectId类，用于处理MongoDB的ObjectId"""
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type,
        _handler,
    ):
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ]),
        ])
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("无效的ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _schema_generator, _field_schema
    ) -> JsonSchemaValue:
        return {"type": "string"}


class StandardResponse(BaseModel):
    """标准响应模型"""
    status: str = "success"
    data: Optional[Any] = None
    message: str = "" 
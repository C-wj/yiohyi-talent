"""
MongoDB 工具类
提供统一的数据序列化、查询、创建、更新等操作方法
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

logger = logging.getLogger(__name__)


class MongoDBUtils:
    """MongoDB 操作工具类"""
    
    @staticmethod
    def convert_objectid_to_str(obj: Any) -> Any:
        """
        递归转换ObjectId为字符串
        
        Args:
            obj: 需要转换的对象
            
        Returns:
            转换后的对象
        """
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: MongoDBUtils.convert_objectid_to_str(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [MongoDBUtils.convert_objectid_to_str(item) for item in obj]
        else:
            return obj
    
    @staticmethod
    def serialize_datetime(obj: Any) -> Any:
        """
        序列化datetime对象为ISO格式字符串
        
        Args:
            obj: 需要序列化的对象
            
        Returns:
            序列化后的对象
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: MongoDBUtils.serialize_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [MongoDBUtils.serialize_datetime(item) for item in obj]
        else:
            return obj
    
    @staticmethod
    def serialize_document(document: Dict[str, Any]) -> Dict[str, Any]:
        """
        完整的MongoDB文档序列化
        
        Args:
            document: MongoDB文档
            
        Returns:
            序列化后的文档
        """
        if not document:
            return document
        
        # 添加字符串ID字段
        if "_id" in document:
            document["id"] = str(document["_id"])
        
        # 转换ObjectId
        document = MongoDBUtils.convert_objectid_to_str(document)
        
        # 转换时间字段
        document = MongoDBUtils.serialize_datetime(document)
        
        return document
    
    @staticmethod
    def validate_object_id(id_string: str) -> bool:
        """
        验证ObjectId格式
        
        Args:
            id_string: 待验证的ID字符串
            
        Returns:
            是否为有效的ObjectId格式
        """
        try:
            ObjectId(id_string)
            return True
        except Exception:
            return False
    
    @staticmethod
    def to_object_id(id_value: Union[str, ObjectId]) -> ObjectId:
        """
        转换为ObjectId
        
        Args:
            id_value: 字符串ID或ObjectId
            
        Returns:
            ObjectId对象
            
        Raises:
            ValueError: 当ID格式无效时
        """
        try:
            if isinstance(id_value, str):
                return ObjectId(id_value)
            elif isinstance(id_value, ObjectId):
                return id_value
            else:
                raise ValueError(f"无效的ID类型: {type(id_value)}")
        except Exception as e:
            logger.error(f"无效的ObjectId: {id_value}, 错误: {str(e)}")
            raise ValueError(f"无效的ID格式: {id_value}")
    
    @staticmethod
    async def get_document_by_id(
        collection: AsyncIOMotorCollection, 
        doc_id: Union[str, ObjectId]
    ) -> Optional[Dict[str, Any]]:
        """
        根据ID获取文档
        
        Args:
            collection: MongoDB集合
            doc_id: 文档ID
            
        Returns:
            序列化后的文档，如果不存在则返回None
        """
        try:
            object_id = MongoDBUtils.to_object_id(doc_id)
            document = await collection.find_one({"_id": object_id})
            
            if not document:
                return None
            
            return MongoDBUtils.serialize_document(document)
        except Exception as e:
            logger.error(f"查询文档失败: {str(e)}, ID: {doc_id}")
            return None
    
    @staticmethod
    async def create_document(
        collection: AsyncIOMotorCollection, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建新文档
        
        Args:
            collection: MongoDB集合
            data: 文档数据
            
        Returns:
            创建的文档（已序列化）
        """
        try:
            # 添加时间戳
            now = datetime.utcnow()
            data["created_at"] = now
            data["updated_at"] = now
            
            # 插入文档
            result = await collection.insert_one(data)
            
            # 获取创建的文档
            document = await collection.find_one({"_id": result.inserted_id})
            
            return MongoDBUtils.serialize_document(document)
        except Exception as e:
            logger.error(f"创建文档失败: {str(e)}")
            raise
    
    @staticmethod
    async def update_document(
        collection: AsyncIOMotorCollection,
        doc_id: Union[str, ObjectId],
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        更新文档
        
        Args:
            collection: MongoDB集合
            doc_id: 文档ID
            update_data: 更新数据
            
        Returns:
            更新后的文档（已序列化），如果不存在则返回None
        """
        try:
            object_id = MongoDBUtils.to_object_id(doc_id)
            
            # 添加更新时间
            update_data["updated_at"] = datetime.utcnow()
            
            # 执行更新
            result = await collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return None
            
            # 返回更新后的文档
            return await MongoDBUtils.get_document_by_id(collection, doc_id)
        except Exception as e:
            logger.error(f"更新文档失败: {str(e)}, ID: {doc_id}")
            raise
    
    @staticmethod
    async def delete_document(
        collection: AsyncIOMotorCollection,
        doc_id: Union[str, ObjectId]
    ) -> bool:
        """
        删除文档
        
        Args:
            collection: MongoDB集合
            doc_id: 文档ID
            
        Returns:
            是否删除成功
        """
        try:
            object_id = MongoDBUtils.to_object_id(doc_id)
            result = await collection.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}, ID: {doc_id}")
            return False
    
    @staticmethod
    async def get_documents_batch(
        collection: AsyncIOMotorCollection,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        批量获取文档
        
        Args:
            collection: MongoDB集合
            filters: 查询过滤条件
            skip: 跳过的文档数
            limit: 限制返回的文档数
            sort: 排序条件
            
        Returns:
            文档列表（已序列化）
        """
        try:
            query = filters or {}
            cursor = collection.find(query).skip(skip).limit(limit)
            
            if sort:
                cursor = cursor.sort(sort)
            
            documents = []
            async for doc in cursor:
                documents.append(MongoDBUtils.serialize_document(doc))
            
            return documents
        except Exception as e:
            logger.error(f"批量查询文档失败: {str(e)}")
            return []
    
    @staticmethod
    async def count_documents(
        collection: AsyncIOMotorCollection,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        统计文档数量
        
        Args:
            collection: MongoDB集合
            filters: 查询过滤条件
            
        Returns:
            文档数量
        """
        try:
            query = filters or {}
            return await collection.count_documents(query)
        except Exception as e:
            logger.error(f"统计文档数量失败: {str(e)}")
            return 0
    
    @staticmethod
    async def document_exists(
        collection: AsyncIOMotorCollection,
        doc_id: Union[str, ObjectId]
    ) -> bool:
        """
        检查文档是否存在
        
        Args:
            collection: MongoDB集合
            doc_id: 文档ID
            
        Returns:
            文档是否存在
        """
        try:
            object_id = MongoDBUtils.to_object_id(doc_id)
            document = await collection.find_one({"_id": object_id}, {"_id": 1})
            return document is not None
        except Exception as e:
            logger.error(f"检查文档存在性失败: {str(e)}, ID: {doc_id}")
            return False


# 便捷的别名
mongodb_utils = MongoDBUtils()

# 导出常用函数
convert_objectid_to_str = MongoDBUtils.convert_objectid_to_str
serialize_document = MongoDBUtils.serialize_document
validate_object_id = MongoDBUtils.validate_object_id
to_object_id = MongoDBUtils.to_object_id 
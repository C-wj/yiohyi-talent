import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, OperationFailure

from app.core.config import settings

# 全局变量
mongo_client: Optional[AsyncIOMotorClient] = None
database: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    """
    连接到MongoDB数据库
    """
    global mongo_client, database
    try:
        # 创建MongoDB客户端
        mongo_client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
            maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
            serverSelectionTimeoutMS=5000  # 降低超时时间，避免长时间等待
        )
        
        # 验证连接
        await mongo_client.admin.command("ping")
        
        # 获取数据库
        database = mongo_client[settings.MONGODB_DB_NAME]
        
        logging.info(f"成功连接到MongoDB: {settings.MONGODB_URI}, 数据库: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        logging.error(f"MongoDB连接失败: {str(e)}")
        # 清理资源
        if mongo_client:
            mongo_client.close()
            mongo_client = None
        database = None
        # 重新抛出异常，让调用者决定如何处理
        raise


async def close_mongo_connection() -> None:
    """
    关闭MongoDB连接
    """
    global mongo_client, database
    if mongo_client:
        mongo_client.close()
        mongo_client = None
        database = None
        logging.info("MongoDB连接已关闭")


def get_database() -> AsyncIOMotorDatabase:
    """
    获取数据库实例
    """
    if database is None:
        logging.warning("MongoDB数据库连接未初始化或连接失败")
        # 返回一个模拟数据库对象，避免程序直接崩溃
        # 这在演示或开发环境中很有用
        class MockDatabase:
            def __getitem__(self, key):
                return MockCollection()
            
            def __getattr__(self, name):
                return MockCollection()
        
        return MockDatabase()
    return database


def get_collection(collection_name: str) -> AsyncIOMotorCollection:
    """
    获取指定集合
    """
    db = get_database()
    return db[collection_name]


# 模拟集合类，用于在数据库连接失败时提供降级服务
class MockCollection:
    """当数据库连接失败时的模拟集合"""
    
    async def find_one(self, *args, **kwargs):
        logging.warning("使用模拟数据：MongoDB连接未建立")
        return None
    
    async def find(self, *args, **kwargs):
        logging.warning("使用模拟数据：MongoDB连接未建立")
        
        class MockCursor:
            async def to_list(self, length):
                return []
            
            async def count_documents(self, *args, **kwargs):
                return 0
        
        return MockCursor()
    
    async def insert_one(self, *args, **kwargs):
        logging.warning("使用模拟数据：MongoDB连接未建立，插入操作被忽略")
        
        class MockInsertResult:
            @property
            def inserted_id(self):
                return "mock_id"
        
        return MockInsertResult()
    
    async def update_one(self, *args, **kwargs):
        logging.warning("使用模拟数据：MongoDB连接未建立，更新操作被忽略")
        return None
    
    async def delete_one(self, *args, **kwargs):
        logging.warning("使用模拟数据：MongoDB连接未建立，删除操作被忽略")
        return None
    
    async def count_documents(self, *args, **kwargs):
        logging.warning("使用模拟数据：MongoDB连接未建立")
        return 0


# 预定义集合名称常量
USERS_COLLECTION = "users"
FAMILIES_COLLECTION = "families"
RECIPES_COLLECTION = "recipes"
MENU_PLANS_COLLECTION = "menu_plans"
SHOPPING_LISTS_COLLECTION = "shopping_lists"
INGREDIENTS_COLLECTION = "ingredients" 
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
        )
        
        # 验证连接
        await mongo_client.admin.command("ping")
        
        # 获取数据库
        database = mongo_client[settings.MONGODB_DB_NAME]
        
        logging.info(f"成功连接到MongoDB: {settings.MONGODB_URI}, 数据库: {settings.MONGODB_DB_NAME}")
    except (ConnectionFailure, OperationFailure) as e:
        logging.error(f"MongoDB连接失败: {str(e)}")
        raise


async def close_mongo_connection() -> None:
    """
    关闭MongoDB连接
    """
    global mongo_client
    if mongo_client:
        mongo_client.close()
        mongo_client = None
        logging.info("MongoDB连接已关闭")


def get_database() -> AsyncIOMotorDatabase:
    """
    获取数据库实例
    """
    if database is None:
        raise ConnectionError("MongoDB数据库连接未初始化")
    return database


def get_collection(collection_name: str) -> AsyncIOMotorCollection:
    """
    获取指定集合
    """
    db = get_database()
    return db[collection_name]


# 预定义集合名称常量
USERS_COLLECTION = "users"
FAMILIES_COLLECTION = "families"
RECIPES_COLLECTION = "recipes"
MENU_PLANS_COLLECTION = "menu_plans"
SHOPPING_LISTS_COLLECTION = "shopping_lists"
INGREDIENTS_COLLECTION = "ingredients" 
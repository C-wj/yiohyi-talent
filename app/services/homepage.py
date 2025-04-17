"""
首页内容服务模块
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from bson import ObjectId

from app.core.exceptions import NotFoundError, DatabaseError
from app.db.mongodb import get_collection
from app.models.homepage import (
    ContentType, 
    ContentStatus, 
    HomeContent,
    SwiperCreate,
    SwiperUpdate,
    CardCreate, 
    CardUpdate,
    ContentFilter
)

# 首页内容集合名称
HOME_CONTENT_COLLECTION = "home_contents"


async def get_content_by_id(content_id: str) -> Optional[Dict[str, Any]]:
    """
    根据ID获取首页内容
    """
    try:
        content_collection = get_collection(HOME_CONTENT_COLLECTION)
        if not ObjectId.is_valid(content_id):
            return None
        
        content = await content_collection.find_one({"_id": content_id})
        return content
    except Exception as e:
        raise DatabaseError(detail=f"获取首页内容失败: {str(e)}")


async def create_content(content_data: Dict[str, Any], creator_id: str) -> Dict[str, Any]:
    """
    创建首页内容
    """
    try:
        content_collection = get_collection(HOME_CONTENT_COLLECTION)
        
        # 设置默认值
        now = datetime.utcnow()
        content_data.setdefault("created_at", now)
        content_data.setdefault("updated_at", now)
        content_data.setdefault("created_by", creator_id)
        content_data.setdefault("updated_by", creator_id)
        
        # 设置内容类型
        if "type" not in content_data:
            content_data["type"] = ContentType.FEATURED.value
        
        # 设置内容状态
        if "status" not in content_data:
            content_data["status"] = ContentStatus.PUBLISHED.value
        
        # 插入数据库
        result = await content_collection.insert_one(content_data)
        created_content = await get_content_by_id(result.inserted_id)
        return created_content
    except Exception as e:
        raise DatabaseError(detail=f"创建首页内容失败: {str(e)}")


async def update_content(content_id: str, update_data: Dict[str, Any], updater_id: str) -> Dict[str, Any]:
    """
    更新首页内容
    """
    try:
        content_collection = get_collection(HOME_CONTENT_COLLECTION)
        
        # 检查内容是否存在
        content = await get_content_by_id(content_id)
        if not content:
            raise NotFoundError(detail=f"内容 {content_id} 不存在")
        
        # 设置更新时间和更新者
        update_data["updated_at"] = datetime.utcnow()
        update_data["updated_by"] = updater_id
        
        # 执行更新
        await content_collection.update_one(
            {"_id": content_id},
            {"$set": update_data}
        )
        
        # 返回更新后的内容
        updated_content = await get_content_by_id(content_id)
        return updated_content
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(detail=f"更新首页内容失败: {str(e)}")


async def delete_content(content_id: str) -> bool:
    """
    删除首页内容
    """
    try:
        content_collection = get_collection(HOME_CONTENT_COLLECTION)
        
        # 检查内容是否存在
        content = await get_content_by_id(content_id)
        if not content:
            raise NotFoundError(detail=f"内容 {content_id} 不存在")
        
        # 执行删除
        result = await content_collection.delete_one({"_id": content_id})
        return result.deleted_count > 0
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(detail=f"删除首页内容失败: {str(e)}")


async def list_contents(
    content_type: Optional[str] = None,
    status: Optional[str] = ContentStatus.PUBLISHED.value,
    skip: int = 0, 
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    获取首页内容列表
    """
    try:
        content_collection = get_collection(HOME_CONTENT_COLLECTION)
        
        # 构建查询条件
        query = {}
        if content_type:
            query["type"] = content_type
        if status:
            query["status"] = status
        
        # 添加时间过滤
        now = datetime.utcnow()
        query.update({
            "$or": [
                # 没有设置开始时间或结束时间
                {"start_time": {"$exists": False}},
                {"end_time": {"$exists": False}},
                # 在有效期内
                {"$and": [
                    {"start_time": {"$lte": now}},
                    {"end_time": {"$gte": now}}
                ]}
            ]
        })
        
        # 查询数据并排序
        cursor = content_collection.find(query).sort("sort_order", 1).skip(skip).limit(limit)
        contents = await cursor.to_list(length=limit)
        return contents
    except Exception as e:
        raise DatabaseError(detail=f"获取首页内容列表失败: {str(e)}")


async def count_contents(content_type: Optional[str] = None, status: Optional[str] = None) -> int:
    """
    获取首页内容数量
    """
    try:
        content_collection = get_collection(HOME_CONTENT_COLLECTION)
        
        # 构建查询条件
        query = {}
        if content_type:
            query["type"] = content_type
        if status:
            query["status"] = status
        
        # 查询数量
        count = await content_collection.count_documents(query)
        return count
    except Exception as e:
        raise DatabaseError(detail=f"获取首页内容数量失败: {str(e)}")


async def get_swipers() -> List[Dict[str, Any]]:
    """
    获取轮播图列表
    """
    return await list_contents(content_type=ContentType.SWIPER.value)


async def get_featured_recipes() -> List[Dict[str, Any]]:
    """
    获取精选菜谱列表
    """
    return await list_contents(content_type=ContentType.FEATURED.value)


async def get_popular_recipes() -> List[Dict[str, Any]]:
    """
    获取热门菜谱列表
    """
    return await list_contents(content_type=ContentType.POPULAR.value)


async def create_swiper(swiper_data: SwiperCreate, creator_id: str) -> Dict[str, Any]:
    """
    创建轮播图
    """
    content_data = swiper_data.dict()
    content_data["type"] = ContentType.SWIPER.value
    return await create_content(content_data, creator_id)


async def create_card(card_data: CardCreate, card_type: ContentType, creator_id: str) -> Dict[str, Any]:
    """
    创建内容卡片
    """
    content_data = card_data.dict()
    content_data["type"] = card_type.value
    return await create_content(content_data, creator_id) 
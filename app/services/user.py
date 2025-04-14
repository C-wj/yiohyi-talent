from datetime import datetime
from typing import Dict, List, Optional, Any

from bson import ObjectId

from app.core.exceptions import NotFoundError, DatabaseError
from app.db.mongodb import get_collection, USERS_COLLECTION
from app.models.user import User, UserProfile, DietaryPreference, Gender
from app.schemas.user import UserCreate, UserUpdate


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    根据ID获取用户
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        if not ObjectId.is_valid(user_id):
            return None
        
        user = await user_collection.find_one({"_id": user_id})
        return user
    except Exception as e:
        raise DatabaseError(detail=f"获取用户失败: {str(e)}")


async def get_user_by_openid(openid: str) -> Optional[Dict[str, Any]]:
    """
    根据微信OpenID获取用户
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        user = await user_collection.find_one({"openid": openid})
        return user
    except Exception as e:
        raise DatabaseError(detail=f"获取用户失败: {str(e)}")


async def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建新用户
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        
        # 检查用户是否已存在
        if "openid" in user_data:
            existing_user = await get_user_by_openid(user_data["openid"])
            if existing_user:
                return existing_user
        
        # 设置默认值
        now = datetime.utcnow()
        user_data.setdefault("created_at", now)
        user_data.setdefault("updated_at", now)
        
        # 确保profile字段存在
        if "profile" not in user_data:
            user_data["profile"] = {
                "nickname": f"用户{user_data['openid'][-6:]}",
                "gender": Gender.UNKNOWN.value
            }
        
        result = await user_collection.insert_one(user_data)
        created_user = await get_user_by_id(result.inserted_id)
        return created_user
    except Exception as e:
        raise DatabaseError(detail=f"创建用户失败: {str(e)}")


async def update_user(user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新用户信息
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        
        # 检查用户是否存在
        user = await get_user_by_id(user_id)
        if not user:
            raise NotFoundError(detail=f"用户 {user_id} 不存在")
        
        # 设置更新时间
        update_data["updated_at"] = datetime.utcnow()
        
        # 执行更新
        await user_collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        # 返回更新后的用户
        updated_user = await get_user_by_id(user_id)
        return updated_user
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(detail=f"更新用户失败: {str(e)}")


async def list_users(skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    获取用户列表
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        query = filters or {}
        cursor = user_collection.find(query).skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        return users
    except Exception as e:
        raise DatabaseError(detail=f"获取用户列表失败: {str(e)}")


async def count_users(filters: Dict[str, Any] = None) -> int:
    """
    获取用户数量
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        query = filters or {}
        count = await user_collection.count_documents(query)
        return count
    except Exception as e:
        raise DatabaseError(detail=f"获取用户数量失败: {str(e)}")


async def delete_user(user_id: str) -> bool:
    """
    删除用户
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        
        # 检查用户是否存在
        user = await get_user_by_id(user_id)
        if not user:
            raise NotFoundError(detail=f"用户 {user_id} 不存在")
        
        # 执行删除
        result = await user_collection.delete_one({"_id": user_id})
        return result.deleted_count > 0
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(detail=f"删除用户失败: {str(e)}")


async def update_user_last_login(user_id: str) -> None:
    """
    更新用户最后登录时间
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        await user_collection.update_one(
            {"_id": user_id},
            {"$set": {"last_login": datetime.utcnow()}}
        )
    except Exception as e:
        # 这里只记录错误但不抛出异常，避免影响登录流程
        print(f"更新用户最后登录时间失败: {str(e)}") 
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from bson import ObjectId
from fastapi import HTTPException, status

from app.core.exceptions import NotFoundError, DatabaseError
from app.db.mongodb import get_collection, USERS_COLLECTION, get_database
from app.models.user import User, UserProfile, Gender,UserCreate, UserUpdate

logger = logging.getLogger(__name__)

async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    根据用户ID获取用户信息
    
    Args:
        user_id: 用户ID
        
    Returns:
        Optional[Dict[str, Any]]: 用户信息
    """
    db = get_database()
    user_collection = db[User.Config.collection]
    
    user = await user_collection.find_one({"_id": user_id})
    if not user:
        return None
    
    # 转换ObjectId为字符串
    user["id"] = str(user.pop("_id"))
    
    return user


async def get_user_by_openid(openid: str) -> Optional[Dict[str, Any]]:
    """
    根据微信openid获取用户
    
    Args:
        openid: 微信openid
        
    Returns:
        Optional[Dict[str, Any]]: 用户信息
    """
    db = get_database()
    user_collection = db[User.Config.collection]
    
    user = await user_collection.find_one({"openid": openid})
    if not user:
        return None
    
    # 转换ObjectId为字符串
    user["id"] = str(user.pop("_id"))
    
    return user


async def get_user_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """
    根据手机号获取用户
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        user = await user_collection.find_one({"phone": phone})
        return user
    except Exception as e:
        raise DatabaseError(detail=f"获取用户失败: {str(e)}")


async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    根据用户名获取用户
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        user = await user_collection.find_one({"username": username})
        return user
    except Exception as e:
        raise DatabaseError(detail=f"获取用户失败: {str(e)}")


async def get_user_by_account(account: str) -> Optional[Dict[str, Any]]:
    """
    根据账号获取用户
    账号可以是手机号、用户名或邮箱
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        # 尝试多种可能的账号类型
        user = await user_collection.find_one({
            "$or": [
                {"phone": account},
                {"username": account},
                {"email": account}
            ]
        })
        return user
    except Exception as e:
        raise DatabaseError(detail=f"获取用户失败: {str(e)}")


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    根据邮箱获取用户
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        user = await user_collection.find_one({"email": email})
        return user
    except Exception as e:
        raise DatabaseError(detail=f"获取用户失败: {str(e)}")


async def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建新用户
    
    Args:
        user_data: 用户数据
        
    Returns:
        Dict[str, Any]: 创建的用户信息
    """
    # 确保必须的字段存在（openid或username）
    if "openid" not in user_data and "username" not in user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少必要的用户信息"
        )
    
    # 创建默认的用户资料
    if "profile" not in user_data:
        # 生成默认昵称
        if "openid" in user_data:
            default_nickname = f"用户{user_data['openid'][-6:]}"
        else:
            default_nickname = f"用户{user_data['username']}"
        user_data["profile"] = UserProfile(nickname=default_nickname).dict()
    
    # 添加时间戳
    user_data["created_at"] = datetime.utcnow()
    user_data["updated_at"] = datetime.utcnow()
    
    db = get_database()
    user_collection = db[User.Config.collection]
    
    existing_user = None
    
    # 检查是否已存在相同用户
    if "openid" in user_data:
        existing_user = await user_collection.find_one({"openid": user_data["openid"]})
    elif "username" in user_data:
        existing_user = await user_collection.find_one({"username": user_data["username"]})
    
    if existing_user:
        # 更新用户信息
        await user_collection.update_one(
            {"_id": existing_user["_id"]},
            {"$set": {
                **user_data,
                "updated_at": datetime.utcnow(),
                "_id": existing_user["_id"]  # 保持ID不变
            }}
        )
        user = await user_collection.find_one({"_id": existing_user["_id"]})
    else:
        # 新建用户
        result = await user_collection.insert_one(user_data)
        user = await user_collection.find_one({"_id": result.inserted_id})
    
    # 转换ObjectId为字符串
    if "_id" in user:
        user["id"] = str(user.pop("_id"))
    
    return user


async def update_user(user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    更新用户信息
    
    Args:
        user_id: 用户ID
        update_data: 更新数据
        
    Returns:
        Optional[Dict[str, Any]]: 更新后的用户信息
    """
    db = get_database()
    user_collection = db[User.Config.collection]
    
    # 添加更新时间
    update_data["updated_at"] = datetime.utcnow()
    
    await user_collection.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )
    
    # 返回更新后的用户信息
    updated_user = await user_collection.find_one({"_id": user_id})
    if not updated_user:
        return None
    
    # 转换ObjectId为字符串
    updated_user["id"] = str(updated_user.pop("_id"))
    
    return updated_user


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
        result = await user_collection.delete_one({"_id": ObjectId(user_id)})
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
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.utcnow()}}
        )
    except Exception as e:
        # 这里只记录错误但不抛出异常，避免影响登录流程
        print(f"更新用户最后登录时间失败: {str(e)}")


async def update_user_stats(user_id: str, stat_type: str, value: int = 1) -> Dict[str, Any]:
    """
    更新用户统计数据
    
    参数:
        user_id: 用户ID
        stat_type: 统计类型 (recipe_count, favorite_count, order_count, followers_count, following_count)
        value: 变化值 (默认+1, 传入负数表示减少)
        
    返回:
        更新后的用户信息
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        
        # 检查用户是否存在
        user = await get_user_by_id(user_id)
        if not user:
            raise NotFoundError(detail=f"用户 {user_id} 不存在")
        
        # 构建统计字段路径
        stat_field = f"stats.{stat_type}"
        
        # 执行更新
        await user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$inc": {stat_field: value},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        # 返回更新后的用户
        updated_user = await get_user_by_id(user_id)
        return updated_user
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(detail=f"更新用户统计数据失败: {str(e)}")


async def update_user_rating(user_id: str, rating: float) -> Dict[str, Any]:
    """
    更新用户评分
    
    参数:
        user_id: 用户ID
        rating: 新增评分 (1-5)
        
    返回:
        更新后的用户信息
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        
        # 检查用户是否存在
        user = await get_user_by_id(user_id)
        if not user:
            raise NotFoundError(detail=f"用户 {user_id} 不存在")
        
        # 获取当前评分和评价数
        current_avg = user.get("stats", {}).get("rating_avg", 0)
        current_count = user.get("stats", {}).get("review_count", 0)
        
        # 计算新的平均评分
        new_count = current_count + 1
        new_avg = ((current_avg * current_count) + rating) / new_count if new_count > 0 else rating
        
        # 四舍五入到一位小数
        new_avg = round(new_avg, 1)
        
        # 执行更新
        await user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "stats.rating_avg": new_avg,
                    "stats.review_count": new_count,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # 返回更新后的用户
        updated_user = await get_user_by_id(user_id)
        return updated_user
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(detail=f"更新用户评分失败: {str(e)}") 
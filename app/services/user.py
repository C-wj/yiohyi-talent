from datetime import datetime
from typing import Dict, List, Optional, Any

from bson import ObjectId

from app.core.exceptions import NotFoundError, DatabaseError
from app.db.mongodb import get_collection, USERS_COLLECTION
from app.models.user import User, UserProfile, Gender
from app.schemas.user import UserCreate, UserUpdate


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    根据ID获取用户
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        if not ObjectId.is_valid(user_id):
            return None
        
        user = await user_collection.find_one({"_id": ObjectId(user_id)})
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
    """
    try:
        user_collection = get_collection(USERS_COLLECTION)
        
        # 设置默认值
        now = datetime.utcnow()
        user_data.setdefault("created_at", now)
        user_data.setdefault("updated_at", now)
        user_data.setdefault("last_login", now)
        
        # 确保profile字段存在
        if "profile" not in user_data:
            user_data["profile"] = {
                "nickname": f"用户{user_data.get('username', str(ObjectId()))[-6:]}",
                "gender": Gender.UNKNOWN.value
            }
        
        # 确保stats字段存在
        if "stats" not in user_data:
            user_data["stats"] = {
                "recipe_count": 0,
                "favorite_count": 0,
                "order_count": 0,
                "followers_count": 0,
                "following_count": 0
            }
        
        # 插入用户数据
        result = await user_collection.insert_one(user_data)
        if not result.inserted_id:
            raise DatabaseError(detail="创建用户失败")
            
        # 获取创建的用户
        created_user = await get_user_by_id(str(result.inserted_id))
        if not created_user:
            raise DatabaseError(detail="无法获取创建的用户")
            
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
            {"_id": ObjectId(user_id)},
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
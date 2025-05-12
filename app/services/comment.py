from datetime import datetime
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
import uuid
from bson import ObjectId

from app.db.mongodb import get_collection, RECIPES_COLLECTION
from app.models.comment import CommentCreate, CommentResponse, UserBrief

# 集合常量
COMMENTS_COLLECTION = "comments"
USERS_COLLECTION = "users"
LIKES_COLLECTION = "comment_likes"


async def create_comment(recipe_id: str, comment_data: CommentCreate, current_user: dict) -> CommentResponse:
    """
    创建菜谱评论
    
    参数:
        recipe_id: 菜谱ID
        comment_data: 评论数据
        current_user: 当前用户信息
        
    返回:
        新创建的评论
    """
    # 获取集合
    recipes_collection = get_collection(RECIPES_COLLECTION)
    comments_collection = get_collection(COMMENTS_COLLECTION)
    
    try:
        # 转换菜谱ID为ObjectId
        recipe_object_id = ObjectId(recipe_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的菜谱ID"
        )
    
    # 检查菜谱是否存在
    recipe = await recipes_collection.find_one({"_id": recipe_object_id})
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜谱不存在"
        )
    
    # 创建评论数据
    now = datetime.utcnow()
    new_comment = {
        "_id": str(uuid.uuid4()),
        "recipe_id": recipe_id,
        "user_id": str(current_user["_id"]),
        "content": comment_data.content,
        "rating": comment_data.rating,
        "images": comment_data.images or [],
        "likes": 0,
        "created_at": now,
        "updated_at": now
    }
    
    # 插入评论到数据库
    await comments_collection.insert_one(new_comment)
    
    # 更新菜谱的评论计数和平均评分
    current_rating = recipe.get("stats", {}).get("ratingAvg", 0)
    current_count = recipe.get("stats", {}).get("ratingCount", 0)
    
    # 计算新的平均评分
    new_count = current_count + 1
    new_rating = ((current_rating * current_count) + comment_data.rating) / new_count
    
    await recipes_collection.update_one(
        {"_id": recipe_object_id},
        {
            "$inc": {"stats.commentCount": 1},
            "$set": {
                "stats.ratingAvg": new_rating,
                "stats.ratingCount": new_count,
                "updated_at": now
            }
        }
    )
    
    # 构建响应
    user_brief = UserBrief(
        id=str(current_user["_id"]),
        name=current_user["profile"]["nickname"],
        avatar=current_user["profile"].get("avatar")
    )
    
    return CommentResponse(
        id=new_comment["_id"],
        user=user_brief,
        recipe_id=recipe_id,
        content=comment_data.content,
        rating=comment_data.rating,
        images=comment_data.images or [],
        likes=0,
        created_at=now,
        updated_at=now
    )


async def get_recipe_comments(
    recipe_id: str, 
    page: int = 1, 
    limit: int = 10
) -> Tuple[List[CommentResponse], int]:
    """
    获取菜谱评论
    
    参数:
        recipe_id: 菜谱ID
        page: 页码
        limit: 每页数量
        
    返回:
        评论列表及总数
    """
    # 获取集合
    recipes_collection = get_collection(RECIPES_COLLECTION)
    comments_collection = get_collection(COMMENTS_COLLECTION)
    users_collection = get_collection(USERS_COLLECTION)
    
    try:
        # 转换菜谱ID为ObjectId
        recipe_object_id = ObjectId(recipe_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的菜谱ID"
        )
    
    # 检查菜谱是否存在
    recipe = await recipes_collection.find_one({"_id": recipe_object_id})
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜谱不存在"
        )
    
    # 计算分页
    skip = (page - 1) * limit
    
    # 查询评论
    cursor = comments_collection.find({"recipe_id": recipe_id})
    
    # 获取总数
    total = await comments_collection.count_documents({"recipe_id": recipe_id})
    
    # 应用分页并按时间倒序排序
    cursor = cursor.sort("created_at", -1).skip(skip).limit(limit)
    
    # 获取评论列表
    comments_list = []
    async for comment in cursor:
        try:
            # 转换用户ID为ObjectId
            user_object_id = ObjectId(comment["user_id"])
            # 获取评论用户信息
            user = await users_collection.find_one({"_id": user_object_id})
            
            if user:
                user_brief = UserBrief(
                    id=str(user["_id"]),
                    name=user["profile"]["nickname"],
                    avatar=user["profile"].get("avatar")
                )
                
                comment_response = CommentResponse(
                    id=str(comment["_id"]),
                    user=user_brief,
                    recipe_id=comment["recipe_id"],
                    content=comment["content"],
                    rating=comment["rating"],
                    images=comment.get("images"),
                    likes=comment.get("likes", 0),
                    created_at=comment["created_at"],
                    updated_at=comment["updated_at"]
                )
                comments_list.append(comment_response)
        except Exception as e:
            print(f"处理评论时出错: {str(e)}")
            continue
    
    return comments_list, total 

async def delete_comment(recipe_id: str, comment_id: str, current_user: dict) -> bool:
    comments_collection = get_collection(COMMENTS_COLLECTION)
    comment = await comments_collection.find_one({"_id": comment_id, "recipe_id": recipe_id})
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    # 仅作者或管理员可删
    if str(comment["user_id"]) != str(current_user["_id"]) and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="无权删除该评论")
    result = await comments_collection.delete_one({"_id": comment_id})
    return result.deleted_count == 1

async def like_comment(comment_id: str, user_id: str) -> bool:
    likes_collection = get_collection(LIKES_COLLECTION)
    comments_collection = get_collection(COMMENTS_COLLECTION)
    # 防止重复点赞
    exists = await likes_collection.find_one({"comment_id": comment_id, "user_id": user_id})
    if exists:
        return False
    await likes_collection.insert_one({"comment_id": comment_id, "user_id": user_id, "created_at": datetime.utcnow()})
    await comments_collection.update_one({"_id": comment_id}, {"$inc": {"likes": 1}})
    return True

async def unlike_comment(comment_id: str, user_id: str) -> bool:
    likes_collection = get_collection(LIKES_COLLECTION)
    comments_collection = get_collection(COMMENTS_COLLECTION)
    result = await likes_collection.delete_one({"comment_id": comment_id, "user_id": user_id})
    if result.deleted_count:
        await comments_collection.update_one({"_id": comment_id}, {"$inc": {"likes": -1}})
        return True
    return False

async def reply_comment(recipe_id: str, parent_id: str, comment_data: CommentCreate, current_user: dict) -> CommentResponse:
    comments_collection = get_collection(COMMENTS_COLLECTION)
    recipes_collection = get_collection(RECIPES_COLLECTION)
    # 检查父评论是否存在
    parent = await comments_collection.find_one({"_id": parent_id, "recipe_id": recipe_id})
    if not parent:
        raise HTTPException(status_code=404, detail="父评论不存在")
    # 检查菜谱是否存在
    recipe = await recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    if not recipe:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    now = datetime.utcnow()
    new_comment = {
        "_id": str(uuid.uuid4()),
        "recipe_id": recipe_id,
        "user_id": str(current_user["_id"]),
        "content": comment_data.content,
        "rating": comment_data.rating,
        "images": comment_data.images or [],
        "likes": 0,
        "parent_id": parent_id,
        "created_at": now,
        "updated_at": now
    }
    await comments_collection.insert_one(new_comment)
    # 构建响应
    user_brief = UserBrief(
        id=str(current_user["_id"]),
        name=current_user["profile"]["nickname"],
        avatar=current_user["profile"].get("avatar")
    )
    return CommentResponse(
        id=new_comment["_id"],
        user=user_brief,
        recipe_id=recipe_id,
        content=comment_data.content,
        rating=comment_data.rating,
        images=comment_data.images or [],
        likes=0,
        created_at=now,
        updated_at=now
    )

async def get_comment_by_id(recipe_id: str, comment_id: str) -> Optional[CommentResponse]:
    comments_collection = get_collection(COMMENTS_COLLECTION)
    users_collection = get_collection(USERS_COLLECTION)
    comment = await comments_collection.find_one({"_id": comment_id, "recipe_id": recipe_id})
    if not comment:
        return None
    user = await users_collection.find_one({"_id": ObjectId(comment["user_id"])})
    if user:
        user_brief = UserBrief(
            id=str(user["_id"]),
            name=user["profile"]["nickname"],
            avatar=user["profile"].get("avatar")
        )
    else:
        user_brief = UserBrief(id=comment["user_id"], name="未知用户", avatar=None)
    return CommentResponse(
        id=comment["_id"],
        user=user_brief,
        recipe_id=comment["recipe_id"],
        content=comment["content"],
        rating=comment["rating"],
        images=comment.get("images"),
        likes=comment.get("likes", 0),
        created_at=comment["created_at"],
        updated_at=comment["updated_at"]
    ) 
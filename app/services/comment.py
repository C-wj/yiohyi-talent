from datetime import datetime
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
import uuid

from app.db.mongodb import get_collection, RECIPES_COLLECTION
from app.models.comment import CommentCreate, CommentResponse, UserBrief

# 集合常量
COMMENTS_COLLECTION = "comments"
USERS_COLLECTION = "users"


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
    
    # 检查菜谱是否存在
    recipe = await recipes_collection.find_one({"_id": recipe_id})
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
        "user_id": current_user["_id"],
        "content": comment_data.content,
        "rating": comment_data.rating,
        "images": comment_data.images,
        "likes": 0,
        "created_at": now,
        "updated_at": now
    }
    
    # 插入评论到数据库
    await comments_collection.insert_one(new_comment)
    
    # 更新菜谱的评论计数和平均评分
    await recipes_collection.update_one(
        {"_id": recipe_id},
        {
            "$inc": {"review_count": 1, "total_rating": comment_data.rating},
            "$set": {"updated_at": now}
        }
    )
    
    # 构建响应
    user_brief = UserBrief(
        id=current_user["_id"],
        name=current_user["profile"]["nickname"],
        avatar=current_user["profile"].get("avatar")
    )
    
    return CommentResponse(
        id=new_comment["_id"],
        user=user_brief,
        recipe_id=recipe_id,
        content=comment_data.content,
        rating=comment_data.rating,
        images=comment_data.images,
        likes=0,
        created_at=now,
        updated_at=now
    )


async def get_recipe_comments(
    recipe_id: str, 
    page: int = 1, 
    limit: int = 10,
    current_user: Optional[dict] = None
) -> Tuple[List[CommentResponse], int]:
    """
    获取菜谱评论
    
    参数:
        recipe_id: 菜谱ID
        page: 页码
        limit: 每页数量
        current_user: 当前用户信息(可选)
        
    返回:
        评论列表及总数
    """
    # 获取集合
    recipes_collection = get_collection(RECIPES_COLLECTION)
    comments_collection = get_collection(COMMENTS_COLLECTION)
    users_collection = get_collection(USERS_COLLECTION)
    
    # 检查菜谱是否存在
    recipe = await recipes_collection.find_one({"_id": recipe_id})
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
        # 获取评论用户信息
        user = await users_collection.find_one({"_id": comment["user_id"]})
        if user:
            user_brief = UserBrief(
                id=user["_id"],
                name=user["profile"]["nickname"],
                avatar=user["profile"].get("avatar")
            )
            
            comment_response = CommentResponse(
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
            comments_list.append(comment_response)
    
    return comments_list, total 
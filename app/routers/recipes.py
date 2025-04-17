from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pymongo.collection import Collection

from app.core.auth import get_current_user
from app.core.config import settings
from app.db.mongodb import get_collection
from app.models.recipe import (RecipeCreate, RecipeCreator, RecipeModel,
                           RecipeResponse, RecipeSearchParams, RecipeUpdate)
from app.models.user import UserModel
from app.models.comment import (CommentCreate, CommentResponse, CommentsListResponse)

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe: RecipeCreate, 
    current_user: UserModel = Depends(get_current_user),
    recipes_collection: Collection = Depends(get_collection(settings.MONGODB_RECIPE_COLLECTION))
):
    """
    创建新菜谱
    """
    recipe_dict = recipe.dict()
    
    recipe_dict["creator"] = {
        "userId": current_user.id,
        "nickname": current_user.profile.nickname,
        "avatar": current_user.profile.avatar
    }
    
    # 设置创建和更新时间
    now = datetime.now()
    recipe_dict["createdAt"] = now
    recipe_dict["updatedAt"] = now
    
    # 设置统计数据
    recipe_dict["stats"] = {
        "viewCount": 0,
        "favoriteCount": 0,
        "commentCount": 0,
        "cookCount": 0,
        "ratingAvg": 0.0,
        "ratingCount": 0
    }
    
    # 其他默认值
    recipe_dict["isOrigin"] = True
    recipe_dict["sourceId"] = None
    recipe_dict["status"] = "draft"
    
    result = await recipes_collection.insert_one(recipe_dict)
    
    # 获取插入的文档
    created_recipe = await recipes_collection.find_one({"_id": result.inserted_id})
    created_recipe["id"] = str(created_recipe.pop("_id"))
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_recipe)


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: str,
    current_user: Optional[UserModel] = Depends(get_current_user),
    recipes_collection: Collection = Depends(get_collection(settings.MONGODB_RECIPE_COLLECTION))
):
    """
    获取指定ID的菜谱详情
    """
    try:
        recipe = await recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid recipe ID")
    
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    
    # 检查访问权限
    if not recipe.get("isPublic", False) and (
        not current_user or str(recipe["creator"]["userId"]) != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You don't have permission to access this recipe"
        )
    
    # 增加浏览次数
    if current_user and str(recipe["creator"]["userId"]) != current_user.id:
        await recipes_collection.update_one(
            {"_id": ObjectId(recipe_id)},
            {"$inc": {"stats.viewCount": 1}}
        )
        recipe["stats"]["viewCount"] += 1
    
    recipe["id"] = str(recipe.pop("_id"))
    return recipe


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: str,
    recipe_update: RecipeUpdate,
    current_user: UserModel = Depends(get_current_user),
    recipes_collection: Collection = Depends(get_collection(settings.MONGODB_RECIPE_COLLECTION))
):
    """
    更新菜谱信息
    """
    try:
        existing_recipe = await recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid recipe ID")
    
    if not existing_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    
    # 验证权限
    if str(existing_recipe["creator"]["userId"]) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You don't have permission to update this recipe"
        )
    
    # 更新字段
    update_data = {k: v for k, v in recipe_update.dict(exclude_unset=True).items()}
    
    if update_data:
        update_data["updatedAt"] = datetime.now()
        result = await recipes_collection.update_one(
            {"_id": ObjectId(recipe_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED,
                detail="Recipe was not modified"
            )
    
    # 获取更新后的菜谱
    updated_recipe = await recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    updated_recipe["id"] = str(updated_recipe.pop("_id"))
    
    return updated_recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: str,
    current_user: UserModel = Depends(get_current_user),
    recipes_collection: Collection = Depends(get_collection(settings.MONGODB_RECIPE_COLLECTION)),
    permanent: bool = Query(False)
):
    """
    删除菜谱
    
    permanent=True: 永久删除
    permanent=False: 将状态改为"deleted"（软删除）
    """
    try:
        existing_recipe = await recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid recipe ID")
    
    if not existing_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    
    # 验证权限
    if str(existing_recipe["creator"]["userId"]) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You don't have permission to delete this recipe"
        )
    
    if permanent:
        # 永久删除
        await recipes_collection.delete_one({"_id": ObjectId(recipe_id)})
    else:
        # 软删除
        await recipes_collection.update_one(
            {"_id": ObjectId(recipe_id)},
            {"$set": {"status": "deleted", "updatedAt": datetime.now()}}
        )
    
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})


@router.get("", response_model=List[RecipeResponse])
async def search_recipes(
    search_params: RecipeSearchParams = Depends(),
    current_user: Optional[UserModel] = Depends(get_current_user),
    recipes_collection: Collection = Depends(get_collection(settings.MONGODB_RECIPE_COLLECTION))
):
    """
    搜索菜谱
    """
    query = {"status": {"$ne": "deleted"}}
    
    # 根据搜索参数构建查询条件
    if search_params.keyword:
        query["$or"] = [
            {"title": {"$regex": search_params.keyword, "$options": "i"}},
            {"description": {"$regex": search_params.keyword, "$options": "i"}}
        ]
    
    if search_params.tags:
        query["tags"] = {"$in": search_params.tags}
    
    if search_params.category:
        query["category"] = search_params.category
    
    if search_params.cuisine:
        query["cuisine"] = search_params.cuisine
    
    if search_params.difficulty:
        query["difficulty"] = search_params.difficulty
    
    if search_params.maxTime:
        query["totalTime"] = {"$lte": search_params.maxTime}
    
    # 处理公开/私有
    if search_params.isPublic is not None:
        query["isPublic"] = search_params.isPublic
    else:
        # 默认只显示公开菜谱，除非指定了创建者
        if not search_params.creatorId and (not current_user or search_params.creatorId != current_user.id):
            query["isPublic"] = True
    
    # 按创建者筛选
    if search_params.creatorId:
        query["creator.userId"] = search_params.creatorId
    
    # 权限筛选：非公开菜谱只有创建者可见
    if current_user:
        query = {
            "$or": [
                {"isPublic": True},
                {"creator.userId": current_user.id}
            ]
        }
    else:
        query["isPublic"] = True
    
    # 排序
    sort_field = search_params.sortBy
    sort_direction = 1 if search_params.sortDirection == "asc" else -1
    
    if sort_field == "popularity":
        sort_field = "stats.viewCount"
    elif sort_field == "rating":
        sort_field = "stats.ratingAvg"
    
    # 分页
    skip = (search_params.page - 1) * search_params.pageSize
    
    # 执行查询
    cursor = recipes_collection.find(query).sort(sort_field, sort_direction).skip(skip).limit(search_params.pageSize)
    
    recipes = []
    async for recipe in cursor:
        recipe["id"] = str(recipe.pop("_id"))
        recipes.append(recipe)
    
    return recipes


@router.post("/{recipe_id}/favorite", status_code=status.HTTP_200_OK)
async def toggle_favorite(
    recipe_id: str,
    current_user: UserModel = Depends(get_current_user),
    recipes_collection: Collection = Depends(get_collection(settings.MONGODB_RECIPE_COLLECTION)),
    user_collection: Collection = Depends(get_collection(settings.MONGODB_USER_COLLECTION))
):
    """
    收藏/取消收藏菜谱
    """
    try:
        recipe = await recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid recipe ID")
    
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    
    # 检查菜谱是否公开或属于当前用户
    if not recipe.get("isPublic", False) and str(recipe["creator"]["userId"]) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You don't have permission to access this recipe"
        )
    
    # 检查用户是否已收藏该菜谱
    user = await user_collection.find_one(
        {"_id": ObjectId(current_user.id), "favorites": recipe_id}
    )
    
    if user:
        # 已收藏，取消收藏
        await user_collection.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$pull": {"favorites": recipe_id}}
        )
        
        # 减少收藏计数
        await recipes_collection.update_one(
            {"_id": ObjectId(recipe_id)},
            {"$inc": {"stats.favoriteCount": -1}}
        )
        
        return {"favorited": False}
    else:
        # 未收藏，添加收藏
        await user_collection.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$addToSet": {"favorites": recipe_id}}
        )
        
        # 增加收藏计数
        await recipes_collection.update_one(
            {"_id": ObjectId(recipe_id)},
            {"$inc": {"stats.favoriteCount": 1}}
        )
        
        return {"favorited": True}


@router.post("/{recipe_id}/comments", response_model=CommentResponse)
async def add_comment(
    recipe_id: str,
    comment_data: CommentCreate,
    current_user: UserModel = Depends(get_current_user),
    recipes_collection: Collection = Depends(get_collection(settings.MONGODB_RECIPE_COLLECTION)),
    comments_collection: Collection = Depends(get_collection(settings.MONGODB_COMMENT_COLLECTION))
):
    """添加菜谱评论"""
    try:
        recipe = await recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的菜谱ID")
    
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="菜谱不存在")
    
    # 创建评论
    comment = {
        "recipeId": recipe_id,
        "userId": current_user.id,
        "content": comment_data.content,
        "rating": comment_data.rating,
        "images": comment_data.images,
        "createdAt": datetime.now(),
        "likes": 0
    }
    
    result = await comments_collection.insert_one(comment)
    
    # 更新菜谱评论数
    await recipes_collection.update_one(
        {"_id": ObjectId(recipe_id)},
        {"$inc": {"stats.commentCount": 1}}
    )
    
    # 如果提供了评分，更新菜谱评分
    if comment_data.rating:
        # 获取当前评分信息
        current_rating = recipe.get("stats", {}).get("ratingAvg", 0)
        current_count = recipe.get("stats", {}).get("ratingCount", 0)
        
        # 计算新评分
        new_count = current_count + 1
        new_rating = ((current_rating * current_count) + comment_data.rating) / new_count
        
        # 更新评分
        await recipes_collection.update_one(
            {"_id": ObjectId(recipe_id)},
            {"$set": {
                "stats.ratingAvg": new_rating,
                "stats.ratingCount": new_count
            }}
        )
    
    # 获取插入的评论并返回
    created_comment = await comments_collection.find_one({"_id": result.inserted_id})
    created_comment["id"] = str(created_comment.pop("_id"))
    
    # 添加用户信息
    created_comment["user"] = {
        "id": current_user.id,
        "nickname": current_user.profile.nickname,
        "avatar": current_user.profile.avatar
    }
    
    return CommentResponse(
        status="success",
        data=created_comment,
        message="评论添加成功"
    )


@router.get("/{recipe_id}/comments", response_model=CommentsListResponse)
async def get_comments(
    recipe_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    recipes_collection: Collection = Depends(get_collection(settings.MONGODB_RECIPE_COLLECTION)),
    comments_collection: Collection = Depends(get_collection(settings.MONGODB_COMMENT_COLLECTION)),
    users_collection: Collection = Depends(get_collection(settings.MONGODB_USER_COLLECTION))
):
    """获取菜谱评论列表"""
    try:
        recipe = await recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的菜谱ID")
    
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="菜谱不存在")
    
    # 分页查询评论
    skip = (page - 1) * limit
    cursor = comments_collection.find({"recipeId": recipe_id}).sort("createdAt", -1).skip(skip).limit(limit)
    
    comments = []
    async for comment in cursor:
        comment["id"] = str(comment.pop("_id"))
        
        # 获取用户信息
        user = await users_collection.find_one({"_id": ObjectId(comment["userId"])})
        if user:
            comment["user"] = {
                "id": str(user["_id"]),
                "nickname": user.get("profile", {}).get("nickname", "用户"),
                "avatar": user.get("profile", {}).get("avatar", "")
            }
        else:
            comment["user"] = {
                "id": comment["userId"],
                "nickname": "未知用户",
                "avatar": ""
            }
        
        comments.append(comment)
    
    # 获取评论总数
    total_comments = await comments_collection.count_documents({"recipeId": recipe_id})
    
    return CommentsListResponse(
        status="success",
        data={
            "list": comments,
            "pagination": {
                "total": total_comments,
                "page": page,
                "limit": limit,
                "pages": (total_comments + limit - 1) // limit
            }
        },
        message="获取评论成功"
    ) 
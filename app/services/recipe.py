from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
from bson import ObjectId
from fastapi import HTTPException, status

from app.db.mongodb import get_collection
from app.models.recipe import RecipeCreate, RecipeUpdate, RecipeSearchParams, RecipeCreator


async def create_recipe(recipe_data: RecipeCreate, current_user: dict) -> dict:
    """
    创建新菜谱
    
    Args:
        recipe_data: 菜谱创建数据
        current_user: 当前用户信息
        
    Returns:
        创建的菜谱信息
    """
    # 获取集合
    recipes_collection = get_collection("recipes")
    users_collection = get_collection("users")
    
    # 创建菜谱创建者信息
    creator = RecipeCreator(
        userId=str(current_user["_id"]),
        nickname=current_user["profile"]["nickname"],
        avatar=current_user["profile"].get("avatar")
    )
    
    # 构建菜谱文档
    now = datetime.now()
    recipe_doc = {
        "title": recipe_data.title,
        "coverImage": recipe_data.coverImage,
        "description": recipe_data.description,
        "tags": recipe_data.tags,
        "category": recipe_data.category,
        "cuisine": recipe_data.cuisine,
        "difficulty": recipe_data.difficulty,
        "prepTime": recipe_data.prepTime,
        "cookTime": recipe_data.cookTime,
        "totalTime": recipe_data.totalTime,
        "servings": recipe_data.servings,
        "creator": creator.dict(),
        "ingredients": [ingredient.dict() for ingredient in recipe_data.ingredients],
        "steps": [step.dict() for step in recipe_data.steps],
        "nutrition": recipe_data.nutrition.dict() if recipe_data.nutrition else None,
        "tips": recipe_data.tips,
        "isPublic": recipe_data.isPublic,
        "isOrigin": True,
        "sourceId": None,
        "status": "draft",
        "stats": {
            "viewCount": 0,
            "favoriteCount": 0,
            "commentCount": 0,
            "cookCount": 0,
            "ratingAvg": 0.0,
            "ratingCount": 0
        },
        "createdAt": now,
        "updatedAt": now
    }
    
    # 插入菜谱文档
    result = await recipes_collection.insert_one(recipe_doc)
    
    # 更新用户的菜谱计数
    await users_collection.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$inc": {"stats.recipeCount": 1}}
    )
    
    # 获取创建的菜谱
    created_recipe = await recipes_collection.find_one({"_id": result.inserted_id})
    
    # 转换_id为字符串
    created_recipe["id"] = str(created_recipe.pop("_id"))
    
    return created_recipe


async def get_recipe_by_id(recipe_id: str, current_user: Optional[dict] = None) -> Optional[dict]:
    """
    根据ID获取菜谱详情
    
    Args:
        recipe_id: 菜谱ID
        current_user: 当前用户信息(可选)
        
    Returns:
        菜谱详情或None(如果不存在)
    """
    # 获取集合
    recipes_collection = get_collection("recipes")
    favorites_collection = get_collection("favorites")
    
    try:
        # 转换字符串ID为ObjectId
        recipe_object_id = ObjectId(recipe_id)
    except Exception as e:
        # ID格式无效
        print(f"无效的ObjectId格式: {recipe_id}, 错误: {str(e)}")
        return None
    
    # 查询菜谱
    try:
        recipe = await recipes_collection.find_one({"_id": recipe_object_id})
        
        if not recipe:
            return None
        
        # 所有菜谱都允许公开访问，不再检查isPublic字段
        
        # 增加浏览次数
        await recipes_collection.update_one(
            {"_id": recipe_object_id},
            {"$inc": {"stats.viewCount": 1}}
        )
        
        # 如果用户已登录，检查是否已收藏
        if current_user:
            favorite = await favorites_collection.find_one({
                "userId": str(current_user["_id"]),
                "recipeId": recipe_id
            })
            recipe["is_favorite"] = favorite is not None
        else:
            recipe["is_favorite"] = False
        
        # 转换_id为字符串
        recipe["id"] = str(recipe.pop("_id"))
        
        return recipe
    except Exception as e:
        print(f"查询菜谱时出错: {str(e)}")
        return None


async def update_recipe(recipe_id: str, recipe_data: RecipeUpdate, current_user: dict) -> Optional[dict]:
    """
    更新菜谱信息
    
    Args:
        recipe_id: 菜谱ID
        recipe_data: 更新数据
        current_user: 当前用户信息
        
    Returns:
        更新后的菜谱或None(如果不存在或无权限)
    """
    # 获取集合
    recipes_collection = get_collection("recipes")
    
    try:
        # 转换字符串ID为ObjectId
        recipe_object_id = ObjectId(recipe_id)
    except:
        # ID格式无效
        return None
    
    # 查询菜谱
    recipe = await recipes_collection.find_one({"_id": recipe_object_id})
    
    if not recipe:
        return None
    
    # 检查更新权限(只有创建者可以更新)
    if str(recipe["creator"]["userId"]) != str(current_user["_id"]):
        # 检查用户是否有管理员权限
        if "admin" not in current_user.get("roles", []):
            return None
    
    # 构建更新文档
    update_doc = {}
    update_fields = recipe_data.dict(exclude_unset=True)
    
    # 只更新提供的字段
    if update_fields:
        for field, value in update_fields.items():
            if value is not None:
                # 对于复杂对象，需要转换为字典
                if hasattr(value, "dict"):
                    update_doc[field] = value.dict()
                elif isinstance(value, list) and value and hasattr(value[0], "dict"):
                    update_doc[field] = [item.dict() for item in value]
                else:
                    update_doc[field] = value
    
    # 添加更新时间
    update_doc["updatedAt"] = datetime.now()
    
    # 执行更新
    await recipes_collection.update_one(
        {"_id": recipe_object_id},
        {"$set": update_doc}
    )
    
    # 获取更新后的菜谱
    updated_recipe = await recipes_collection.find_one({"_id": recipe_object_id})
    
    # 转换_id为字符串
    updated_recipe["id"] = str(updated_recipe.pop("_id"))
    
    return updated_recipe


async def favorite_recipe(recipe_id: str, current_user: dict) -> dict:
    """
    收藏/取消收藏菜谱
    
    Args:
        recipe_id: 菜谱ID
        current_user: 当前用户信息
        
    Returns:
        操作结果
    """
    # 获取集合
    recipes_collection = get_collection("recipes")
    favorites_collection = get_collection("favorites")
    users_collection = get_collection("users")
    
    try:
        # 转换字符串ID为ObjectId(用于检查菜谱是否存在)
        recipe_object_id = ObjectId(recipe_id)
    except:
        # ID格式无效
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的菜谱ID"
        )
    
    # 查询菜谱是否存在
    recipe = await recipes_collection.find_one({"_id": recipe_object_id})
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜谱不存在"
        )
    
    # 检查是否已收藏
    favorite = await favorites_collection.find_one({
        "userId": str(current_user["_id"]),
        "recipeId": recipe_id
    })
    
    if favorite:
        # 已收藏，取消收藏
        await favorites_collection.delete_one({
            "userId": str(current_user["_id"]),
            "recipeId": recipe_id
        })
        
        # 减少收藏计数
        await recipes_collection.update_one(
            {"_id": recipe_object_id},
            {"$inc": {"stats.favoriteCount": -1}}
        )
        
        # 减少用户收藏计数
        await users_collection.update_one(
            {"_id": ObjectId(current_user["_id"])},
            {"$inc": {"stats.favoriteCount": -1}}
        )
        
        return {"is_favorite": False}
    else:
        # 未收藏，添加收藏
        await favorites_collection.insert_one({
            "userId": str(current_user["_id"]),
            "recipeId": recipe_id,
            "createdAt": datetime.now()
        })
        
        # 增加收藏计数
        await recipes_collection.update_one(
            {"_id": recipe_object_id},
            {"$inc": {"stats.favoriteCount": 1}}
        )
        
        # 增加用户收藏计数
        await users_collection.update_one(
            {"_id": ObjectId(current_user["_id"])},
            {"$inc": {"stats.favoriteCount": 1}}
        )
        
        return {"is_favorite": True}


async def search_recipes(
    params: RecipeSearchParams, 
    current_user: Optional[dict] = None
) -> Tuple[List[dict], int]:
    """
    搜索菜谱
    
    Args:
        params: 搜索参数
        current_user: 当前用户信息(可选)
        
    Returns:
        菜谱列表和总数
    """
    # 获取集合
    recipes_collection = get_collection("recipes")
    favorites_collection = get_collection("favorites")
    
    # 构建查询条件
    query: Dict[str, Any] = {}
    
    # 公开状态过滤
    if params.isPublic is not None:
        query["isPublic"] = params.isPublic
    else:
        # 默认只显示已发布的公开菜谱
        query["isPublic"] = True
        query["status"] = "published"
    
    # 根据关键词搜索标题和描述
    if params.keyword:
        # 使用文本索引或正则表达式
        text_query = {"$regex": params.keyword, "$options": "i"}
        query["$or"] = [
            {"title": text_query},
            {"description": text_query},
            {"tags": params.keyword}
        ]
    
    # 标签过滤
    if params.tags:
        query["tags"] = {"$in": params.tags}
    
    # 分类过滤
    if params.category:
        query["category"] = params.category
    
    # 菜系过滤
    if params.cuisine:
        query["cuisine"] = params.cuisine
    
    # 难度过滤
    if params.difficulty:
        query["difficulty"] = params.difficulty
    
    # 最大时间过滤
    if params.maxTime:
        query["totalTime"] = {"$lte": params.maxTime}
    
    # 创建者过滤
    if params.creatorId:
        query["creator.userId"] = params.creatorId
    
    # 计算分页参数
    skip = (params.page - 1) * params.pageSize
    limit = params.pageSize
    
    # 确定排序方式
    sort_field = "createdAt"
    if params.sortBy == "popularity":
        sort_field = "stats.viewCount"
    elif params.sortBy == "rating":
        sort_field = "stats.ratingAvg"
    
    sort_direction = -1 if params.sortDirection == "desc" else 1
    
    # 查询总数
    total = await recipes_collection.count_documents(query)
    
    # 执行查询
    cursor = recipes_collection.find(query)
    cursor = cursor.sort(sort_field, sort_direction)
    cursor = cursor.skip(skip).limit(limit)
    
    # 获取结果
    recipes = await cursor.to_list(length=limit)
    
    # 处理结果
    for recipe in recipes:
        recipe["id"] = str(recipe.pop("_id"))
        
        # 如果用户已登录，检查是否已收藏
        if current_user:
            favorite = await favorites_collection.find_one({
                "userId": str(current_user["_id"]),
                "recipeId": recipe["id"]
            })
            recipe["is_favorite"] = favorite is not None
        else:
            recipe["is_favorite"] = False
    
    return recipes, total 
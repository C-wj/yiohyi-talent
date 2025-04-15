from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from bson import ObjectId
from fastapi import HTTPException, status

from app.db.mongodb import get_database
from app.models.menu_plan import (
    MenuPlanCreate, 
    MenuPlanUpdate, 
    DishAdd, 
    MenuPlanListParams,
    MealType
)


async def create_menu_plan(plan_data: MenuPlanCreate, current_user: dict) -> dict:
    """
    创建新的菜单计划
    
    Args:
        plan_data: 菜单计划创建数据
        current_user: 当前用户信息
        
    Returns:
        创建的菜单计划信息
    """
    db = await get_database()
    
    # 验证家庭存在并且用户是家庭成员
    family = await db.families.find_one({"_id": ObjectId(plan_data.familyId)})
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="家庭不存在"
        )
    
    # 检查用户是否是家庭成员
    is_member = False
    for member in family.get("members", []):
        if str(member.get("userId")) == str(current_user["_id"]):
            is_member = True
            break
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户不是该家庭成员"
        )
    
    # 构建菜单计划文档
    now = datetime.now()
    plan_doc = {
        "name": plan_data.name,
        "familyId": plan_data.familyId,
        "creatorId": str(current_user["_id"]),
        "date": plan_data.date,
        "meals": [meal.dict() for meal in plan_data.meals],
        "guestCount": plan_data.guestCount,
        "specialNeeds": [need.dict() for need in plan_data.specialNeeds],
        "status": plan_data.status,
        "shoppingListId": None,
        "collaborators": [collab.dict() for collab in plan_data.collaborators],
        "createdAt": now,
        "updatedAt": now,
        "confirmedAt": None
    }
    
    # 插入菜单计划文档
    result = await db.menu_plans.insert_one(plan_doc)
    
    # 获取创建的菜单计划
    created_plan = await db.menu_plans.find_one({"_id": result.inserted_id})
    
    # 转换_id为字符串
    created_plan["id"] = str(created_plan.pop("_id"))
    
    return created_plan


async def get_menu_plan_by_id(plan_id: str, current_user: dict) -> Optional[dict]:
    """
    根据ID获取菜单计划详情
    
    Args:
        plan_id: 菜单计划ID
        current_user: 当前用户信息
        
    Returns:
        菜单计划详情或None(如果不存在或无权访问)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        plan_object_id = ObjectId(plan_id)
    except:
        # ID格式无效
        return None
    
    # 查询菜单计划
    plan = await db.menu_plans.find_one({"_id": plan_object_id})
    
    if not plan:
        return None
    
    # 检查访问权限
    if str(plan["creatorId"]) != str(current_user["_id"]):
        # 检查用户是否是菜单计划的协作者
        is_collaborator = False
        for collaborator in plan.get("collaborators", []):
            if str(collaborator.get("userId")) == str(current_user["_id"]):
                is_collaborator = True
                break
        
        # 检查用户是否是家庭成员
        if not is_collaborator:
            family = await db.families.find_one({"_id": ObjectId(plan["familyId"])})
            if family:
                is_family_member = False
                for member in family.get("members", []):
                    if str(member.get("userId")) == str(current_user["_id"]):
                        is_family_member = True
                        break
                
                if not is_family_member:
                    return None
            else:
                return None
    
    # 转换_id为字符串
    plan["id"] = str(plan.pop("_id"))
    
    return plan


async def update_menu_plan(plan_id: str, plan_data: MenuPlanUpdate, current_user: dict) -> Optional[dict]:
    """
    更新菜单计划信息
    
    Args:
        plan_id: 菜单计划ID
        plan_data: 更新数据
        current_user: 当前用户信息
        
    Returns:
        更新后的菜单计划或None(如果不存在或无权限)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        plan_object_id = ObjectId(plan_id)
    except:
        # ID格式无效
        return None
    
    # 查询菜单计划
    plan = await db.menu_plans.find_one({"_id": plan_object_id})
    
    if not plan:
        return None
    
    # 检查更新权限(创建者或编辑者可以更新)
    has_permission = False
    if str(plan["creatorId"]) == str(current_user["_id"]):
        has_permission = True
    else:
        for collaborator in plan.get("collaborators", []):
            if (str(collaborator.get("userId")) == str(current_user["_id"]) and 
                collaborator.get("role") in ["owner", "editor"]):
                has_permission = True
                break
    
    if not has_permission:
        # 检查用户是否有管理员权限
        if "admin" not in current_user.get("roles", []):
            return None
    
    # 构建更新文档
    update_doc = {}
    update_fields = plan_data.dict(exclude_unset=True)
    
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
    await db.menu_plans.update_one(
        {"_id": plan_object_id},
        {"$set": update_doc}
    )
    
    # 获取更新后的菜单计划
    updated_plan = await db.menu_plans.find_one({"_id": plan_object_id})
    
    # 转换_id为字符串
    updated_plan["id"] = str(updated_plan.pop("_id"))
    
    return updated_plan


async def add_dish_to_menu(plan_id: str, dish_data: DishAdd, current_user: dict) -> Optional[dict]:
    """
    向菜单添加菜品
    
    Args:
        plan_id: 菜单计划ID
        dish_data: 添加的菜品数据
        current_user: 当前用户信息
        
    Returns:
        更新后的菜单计划或None(如果不存在或无权限)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        plan_object_id = ObjectId(plan_id)
    except:
        # ID格式无效
        return None
    
    # 查询菜单计划
    plan = await db.menu_plans.find_one({"_id": plan_object_id})
    
    if not plan:
        return None
    
    # 检查权限
    has_permission = False
    if str(plan["creatorId"]) == str(current_user["_id"]):
        has_permission = True
    else:
        for collaborator in plan.get("collaborators", []):
            if (str(collaborator.get("userId")) == str(current_user["_id"]) and 
                collaborator.get("role") in ["owner", "editor"]):
                has_permission = True
                break
    
    if not has_permission:
        return None
    
    # 获取菜谱信息
    recipe = await db.recipes.find_one({"_id": ObjectId(dish_data.recipeId)})
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜谱不存在"
        )
    
    # 创建要添加的菜品
    dish_detail = {
        "recipeId": dish_data.recipeId,
        "title": recipe["title"],
        "image": recipe.get("coverImage"),
        "servings": dish_data.servings,
        "notes": dish_data.notes
    }
    
    # 检查指定餐类型的餐点是否存在，不存在则创建
    meal_exists = False
    for meal in plan.get("meals", []):
        if meal["type"] == dish_data.mealType:
            meal_exists = True
            break
    
    if not meal_exists:
        # 添加新的餐点类型
        await db.menu_plans.update_one(
            {"_id": plan_object_id},
            {"$push": {"meals": {"type": dish_data.mealType, "time": None, "dishes": []}}}
        )
    
    # 添加菜品到指定餐点
    await db.menu_plans.update_one(
        {"_id": plan_object_id, "meals.type": dish_data.mealType},
        {
            "$push": {"meals.$.dishes": dish_detail},
            "$set": {"updatedAt": datetime.now()}
        }
    )
    
    # 获取更新后的菜单计划
    updated_plan = await db.menu_plans.find_one({"_id": plan_object_id})
    
    # 转换_id为字符串
    updated_plan["id"] = str(updated_plan.pop("_id"))
    
    return updated_plan


async def get_family_menu_plans(
    params: MenuPlanListParams, 
    current_user: dict
) -> Tuple[List[dict], int]:
    """
    获取指定家庭的菜单计划
    
    Args:
        params: 查询参数
        current_user: 当前用户信息
        
    Returns:
        菜单计划列表和总数
    """
    db = await get_database()
    
    # 构建查询条件
    query: Dict[str, Any] = {}
    
    # 家庭ID过滤
    if params.familyId:
        # 验证家庭存在并且用户是家庭成员
        family = await db.families.find_one({"_id": ObjectId(params.familyId)})
        if not family:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="家庭不存在"
            )
        
        # 检查用户是否是家庭成员
        is_member = False
        for member in family.get("members", []):
            if str(member.get("userId")) == str(current_user["_id"]):
                is_member = True
                break
        
        if not is_member and "admin" not in current_user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户不是该家庭成员"
            )
        
        query["familyId"] = params.familyId
    else:
        # 获取用户所有家庭的菜单计划
        families = await db.families.find(
            {"members.userId": str(current_user["_id"])},
            {"_id": 1}
        ).to_list(length=100)
        
        if not families:
            return [], 0
        
        family_ids = [str(family["_id"]) for family in families]
        query["familyId"] = {"$in": family_ids}
    
    # 日期范围过滤
    date_filter = {}
    if params.startDate:
        date_filter["$gte"] = params.startDate
    if params.endDate:
        date_filter["$lte"] = params.endDate
    if date_filter:
        query["date"] = date_filter
    
    # 状态过滤
    if params.status:
        query["status"] = {"$in": params.status}
    
    # 计算分页参数
    skip = (params.page - 1) * params.pageSize
    limit = params.pageSize
    
    # 查询总数
    total = await db.menu_plans.count_documents(query)
    
    # 执行查询
    cursor = db.menu_plans.find(query)
    cursor = cursor.sort("date", -1)  # 默认按日期降序排序
    cursor = cursor.skip(skip).limit(limit)
    
    # 获取结果
    plans = await cursor.to_list(length=limit)
    
    # 处理结果
    for plan in plans:
        plan["id"] = str(plan.pop("_id"))
    
    return plans, total 
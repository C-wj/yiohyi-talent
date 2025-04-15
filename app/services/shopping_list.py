from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from bson import ObjectId
from fastapi import HTTPException, status

from app.db.mongodb import get_database
from app.models.shopping_list import (
    ShoppingListCreate,
    ShoppingListUpdate,
    ShoppingItemAdd,
    ShoppingItemUpdate,
    ShoppingItemBatchUpdate,
    ShoppingListGenerateRequest,
    ShoppingListListParams,
    ShoppingItemStatus,
    ShoppingListStatus,
    ShoppingItem
)


async def create_shopping_list(list_data: ShoppingListCreate, current_user: dict) -> dict:
    """
    创建新的购物清单
    
    Args:
        list_data: 购物清单创建数据
        current_user: 当前用户信息
        
    Returns:
        创建的购物清单信息
    """
    db = await get_database()
    
    # 验证家庭存在并且用户是家庭成员
    family = await db.families.find_one({"_id": ObjectId(list_data.familyId)})
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
    
    # 如果指定了关联的菜单计划，验证其存在
    if list_data.planId:
        plan = await db.menu_plans.find_one({"_id": ObjectId(list_data.planId)})
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="关联的菜单计划不存在"
            )
        
        # 更新菜单计划的shoppingListId字段
        await db.menu_plans.update_one(
            {"_id": ObjectId(list_data.planId)},
            {"$set": {"shoppingListId": "pending"}}  # 先设置为pending，待插入后再更新
        )
    
    # 构建购物清单文档
    now = datetime.now()
    list_date = list_data.date if list_data.date else now
    
    list_doc = {
        "planId": list_data.planId,
        "familyId": list_data.familyId,
        "name": list_data.name,
        "date": list_date,
        "items": [item.dict() for item in list_data.items],
        "totalCost": 0,  # 初始化总成本为0
        "status": ShoppingListStatus.PLANNING,
        "sharedWith": [user.dict() for user in list_data.sharedWith],
        "createdAt": now,
        "updatedAt": now,
        "completedAt": None
    }
    
    # 插入购物清单文档
    result = await db.shopping_lists.insert_one(list_doc)
    
    # 如果指定了关联的菜单计划，更新其shoppingListId字段
    if list_data.planId:
        await db.menu_plans.update_one(
            {"_id": ObjectId(list_data.planId)},
            {"$set": {"shoppingListId": str(result.inserted_id)}}
        )
    
    # 获取创建的购物清单
    created_list = await db.shopping_lists.find_one({"_id": result.inserted_id})
    
    # 转换_id为字符串
    created_list["id"] = str(created_list.pop("_id"))
    
    return created_list


async def get_shopping_list_by_id(list_id: str, current_user: dict) -> Optional[dict]:
    """
    根据ID获取购物清单详情
    
    Args:
        list_id: 购物清单ID
        current_user: 当前用户信息
        
    Returns:
        购物清单详情或None(如果不存在或无权访问)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        list_object_id = ObjectId(list_id)
    except:
        # ID格式无效
        return None
    
    # 查询购物清单
    shopping_list = await db.shopping_lists.find_one({"_id": list_object_id})
    
    if not shopping_list:
        return None
    
    # 检查访问权限
    # 1. 用户是否是创建者(通过家庭成员关系)
    family = await db.families.find_one({"_id": ObjectId(shopping_list["familyId"])})
    if family:
        is_family_member = False
        for member in family.get("members", []):
            if str(member.get("userId")) == str(current_user["_id"]):
                is_family_member = True
                break
        
        if not is_family_member:
            # 2. 用户是否在共享列表中
            is_shared = False
            for share in shopping_list.get("sharedWith", []):
                if str(share.get("userId")) == str(current_user["_id"]):
                    is_shared = True
                    break
            
            if not is_shared:
                return None
    else:
        return None
    
    # 转换_id为字符串
    shopping_list["id"] = str(shopping_list.pop("_id"))
    
    return shopping_list


async def update_shopping_list(list_id: str, list_data: ShoppingListUpdate, current_user: dict) -> Optional[dict]:
    """
    更新购物清单信息
    
    Args:
        list_id: 购物清单ID
        list_data: 更新数据
        current_user: 当前用户信息
        
    Returns:
        更新后的购物清单或None(如果不存在或无权限)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        list_object_id = ObjectId(list_id)
    except:
        # ID格式无效
        return None
    
    # 查询购物清单
    shopping_list = await db.shopping_lists.find_one({"_id": list_object_id})
    
    if not shopping_list:
        return None
    
    # 检查更新权限
    # 1. 用户是否是家庭成员
    family = await db.families.find_one({"_id": ObjectId(shopping_list["familyId"])})
    
    if not family:
        return None
    
    is_family_member = False
    for member in family.get("members", []):
        if str(member.get("userId")) == str(current_user["_id"]):
            is_family_member = True
            break
    
    if not is_family_member:
        # 2. 用户是否在共享列表中且有写权限
        has_write_permission = False
        for share in shopping_list.get("sharedWith", []):
            if str(share.get("userId")) == str(current_user["_id"]) and share.get("permission") == "write":
                has_write_permission = True
                break
        
        if not has_write_permission and "admin" not in current_user.get("roles", []):
            return None
    
    # 构建更新文档
    update_doc = {}
    update_fields = list_data.dict(exclude_unset=True)
    
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
    
    # 计算总成本(如果更新了items)
    if "items" in update_doc:
        total_cost = 0
        for item in update_doc["items"]:
            if item.get("price") is not None and item.get("amount") is not None:
                total_cost += item["price"] * item["amount"]
        update_doc["totalCost"] = total_cost
    
    # 检查是否更新为已完成状态
    if list_data.status == ShoppingListStatus.COMPLETED:
        update_doc["completedAt"] = datetime.now()
    
    # 添加更新时间
    update_doc["updatedAt"] = datetime.now()
    
    # 执行更新
    await db.shopping_lists.update_one(
        {"_id": list_object_id},
        {"$set": update_doc}
    )
    
    # 获取更新后的购物清单
    updated_list = await db.shopping_lists.find_one({"_id": list_object_id})
    
    # 转换_id为字符串
    updated_list["id"] = str(updated_list.pop("_id"))
    
    return updated_list


async def add_item_to_shopping_list(list_id: str, item_data: ShoppingItemAdd, current_user: dict) -> Optional[dict]:
    """
    向购物清单添加项目
    
    Args:
        list_id: 购物清单ID
        item_data: 添加的项目数据
        current_user: 当前用户信息
        
    Returns:
        更新后的购物清单或None(如果不存在或无权限)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        list_object_id = ObjectId(list_id)
    except:
        # ID格式无效
        return None
    
    # 查询购物清单
    shopping_list = await db.shopping_lists.find_one({"_id": list_object_id})
    
    if not shopping_list:
        return None
    
    # 检查权限
    # 1. 用户是否是家庭成员
    family = await db.families.find_one({"_id": ObjectId(shopping_list["familyId"])})
    
    if not family:
        return None
    
    is_family_member = False
    for member in family.get("members", []):
        if str(member.get("userId")) == str(current_user["_id"]):
            is_family_member = True
            break
    
    if not is_family_member:
        # 2. 用户是否在共享列表中且有写权限
        has_write_permission = False
        for share in shopping_list.get("sharedWith", []):
            if str(share.get("userId")) == str(current_user["_id"]) and share.get("permission") == "write":
                has_write_permission = True
                break
        
        if not has_write_permission:
            return None
    
    # 创建要添加的项目
    item = ShoppingItem(
        name=item_data.name,
        category=item_data.category,
        amount=item_data.amount,
        unit=item_data.unit,
        price=item_data.price,
        note=item_data.note,
        recipeId=item_data.recipeId,
        planId=item_data.planId,
        status=ShoppingItemStatus.PENDING,
        checked=False
    )
    
    # 添加项目到购物清单
    await db.shopping_lists.update_one(
        {"_id": list_object_id},
        {
            "$push": {"items": item.dict()},
            "$set": {"updatedAt": datetime.now()}
        }
    )
    
    # 更新总成本
    if item.price is not None and item.amount is not None:
        new_cost = shopping_list["totalCost"] + (item.price * item.amount)
        await db.shopping_lists.update_one(
            {"_id": list_object_id},
            {"$set": {"totalCost": new_cost}}
        )
    
    # 获取更新后的购物清单
    updated_list = await db.shopping_lists.find_one({"_id": list_object_id})
    
    # 转换_id为字符串
    updated_list["id"] = str(updated_list.pop("_id"))
    
    return updated_list


async def update_shopping_item(
    list_id: str, 
    item_index: int, 
    item_data: ShoppingItemUpdate, 
    current_user: dict
) -> Optional[dict]:
    """
    更新购物清单中的项目
    
    Args:
        list_id: 购物清单ID
        item_index: 项目在列表中的索引
        item_data: 更新数据
        current_user: 当前用户信息
        
    Returns:
        更新后的购物清单或None(如果不存在或无权限)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        list_object_id = ObjectId(list_id)
    except:
        # ID格式无效
        return None
    
    # 查询购物清单
    shopping_list = await db.shopping_lists.find_one({"_id": list_object_id})
    
    if not shopping_list:
        return None
    
    # 检查项目索引是否有效
    if item_index < 0 or item_index >= len(shopping_list.get("items", [])):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的项目索引"
        )
    
    # 检查权限
    # 1. 用户是否是家庭成员
    family = await db.families.find_one({"_id": ObjectId(shopping_list["familyId"])})
    
    if not family:
        return None
    
    is_family_member = False
    for member in family.get("members", []):
        if str(member.get("userId")) == str(current_user["_id"]):
            is_family_member = True
            break
    
    if not is_family_member:
        # 2. 用户是否在共享列表中且有写权限
        has_write_permission = False
        for share in shopping_list.get("sharedWith", []):
            if str(share.get("userId")) == str(current_user["_id"]) and share.get("permission") == "write":
                has_write_permission = True
                break
        
        if not has_write_permission:
            return None
    
    # 构建更新文档
    update_fields = item_data.dict(exclude_unset=True)
    
    if not update_fields:
        # 没有需要更新的字段
        return shopping_list
    
    # 更新项目字段
    update_operations = {}
    for field, value in update_fields.items():
        update_operations[f"items.{item_index}.{field}"] = value
    
    # 添加更新时间
    update_operations["updatedAt"] = datetime.now()
    
    # 执行更新
    await db.shopping_lists.update_one(
        {"_id": list_object_id},
        {"$set": update_operations}
    )
    
    # 如果更新了价格或数量，重新计算总成本
    if "price" in update_fields or "amount" in update_fields:
        # 获取所有项目
        updated_list = await db.shopping_lists.find_one({"_id": list_object_id})
        
        # 计算总成本
        total_cost = 0
        for item in updated_list["items"]:
            if item.get("price") is not None and item.get("amount") is not None:
                total_cost += item["price"] * item["amount"]
        
        # 更新总成本
        await db.shopping_lists.update_one(
            {"_id": list_object_id},
            {"$set": {"totalCost": total_cost}}
        )
    
    # 获取更新后的购物清单
    updated_list = await db.shopping_lists.find_one({"_id": list_object_id})
    
    # 转换_id为字符串
    updated_list["id"] = str(updated_list.pop("_id"))
    
    return updated_list


async def batch_update_items(
    list_id: str, 
    batch_update: ShoppingItemBatchUpdate, 
    current_user: dict
) -> Optional[dict]:
    """
    批量更新购物项目状态
    
    Args:
        list_id: 购物清单ID
        batch_update: 批量更新数据
        current_user: 当前用户信息
        
    Returns:
        更新后的购物清单或None(如果不存在或无权限)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        list_object_id = ObjectId(list_id)
    except:
        # ID格式无效
        return None
    
    # 查询购物清单
    shopping_list = await db.shopping_lists.find_one({"_id": list_object_id})
    
    if not shopping_list:
        return None
    
    # 检查项目索引是否有效
    items = shopping_list.get("items", [])
    for index in batch_update.itemIds:
        if index < 0 or index >= len(items):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的项目索引: {index}"
            )
    
    # 检查权限
    # 1. 用户是否是家庭成员
    family = await db.families.find_one({"_id": ObjectId(shopping_list["familyId"])})
    
    if not family:
        return None
    
    is_family_member = False
    for member in family.get("members", []):
        if str(member.get("userId")) == str(current_user["_id"]):
            is_family_member = True
            break
    
    if not is_family_member:
        # 2. 用户是否在共享列表中且有写权限
        has_write_permission = False
        for share in shopping_list.get("sharedWith", []):
            if str(share.get("userId")) == str(current_user["_id"]) and share.get("permission") == "write":
                has_write_permission = True
                break
        
        if not has_write_permission:
            return None
    
    # 构建批量更新操作
    update_operations = {}
    for index in batch_update.itemIds:
        update_operations[f"items.{index}.checked"] = batch_update.checked
    
    # 添加更新时间
    update_operations["updatedAt"] = datetime.now()
    
    # 执行更新
    await db.shopping_lists.update_one(
        {"_id": list_object_id},
        {"$set": update_operations}
    )
    
    # 获取更新后的购物清单
    updated_list = await db.shopping_lists.find_one({"_id": list_object_id})
    
    # 转换_id为字符串
    updated_list["id"] = str(updated_list.pop("_id"))
    
    return updated_list


async def generate_shopping_list(generate_data: ShoppingListGenerateRequest, current_user: dict) -> dict:
    """
    基于菜单计划生成购物清单
    
    Args:
        generate_data: 生成购物清单请求数据
        current_user: 当前用户信息
        
    Returns:
        生成的购物清单
    """
    db = await get_database()
    
    # 验证家庭存在并且用户是家庭成员
    family = await db.families.find_one({"_id": ObjectId(generate_data.familyId)})
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="家庭不存在"
        )
    
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
    
    # 收集所有指定菜单计划中的菜品和食材
    all_ingredients = []
    
    for plan_id in generate_data.planIds:
        try:
            plan = await db.menu_plans.find_one({"_id": ObjectId(plan_id)})
            if not plan:
                continue
            
            # 确保菜单计划属于指定家庭
            if plan["familyId"] != generate_data.familyId:
                continue
            
            # 遍历所有餐点和菜品
            for meal in plan.get("meals", []):
                for dish in meal.get("dishes", []):
                    # 获取菜谱详情
                    recipe = await db.recipes.find_one({"_id": ObjectId(dish["recipeId"])})
                    if not recipe:
                        continue
                    
                    # 计算食材数量
                    servings_ratio = dish["servings"] / recipe.get("servings", 1)
                    
                    # 收集食材
                    for ingredient in recipe.get("ingredients", []):
                        # 跳过可选食材
                        if ingredient.get("optional", False):
                            continue
                        
                        # 计算调整后的食材数量
                        adjusted_amount = None
                        if ingredient.get("amount") is not None:
                            adjusted_amount = ingredient["amount"] * servings_ratio
                        
                        # 创建购物项目
                        shopping_item = {
                            "name": ingredient["name"],
                            "recipeId": dish["recipeId"],
                            "planId": plan_id,
                            "category": ingredient.get("category"),
                            "amount": adjusted_amount,
                            "unit": ingredient.get("unit"),
                            "price": None,
                            "note": ingredient.get("note"),
                            "status": ShoppingItemStatus.PENDING,
                            "checked": False
                        }
                        
                        all_ingredients.append(shopping_item)
        except Exception as e:
            # 如果处理某个菜单计划出错，继续处理下一个
            continue
    
    # 合并相同食材
    merged_ingredients = {}
    
    for item in all_ingredients:
        key = f"{item['name']}_{item.get('unit')}"
        
        if key in merged_ingredients:
            # 合并数量
            if item["amount"] is not None:
                if merged_ingredients[key]["amount"] is None:
                    merged_ingredients[key]["amount"] = item["amount"]
                else:
                    merged_ingredients[key]["amount"] += item["amount"]
            
            # 合并来源
            source_recipes = merged_ingredients[key].get("recipeIds", [])
            if item["recipeId"] not in source_recipes:
                source_recipes.append(item["recipeId"])
                merged_ingredients[key]["recipeIds"] = source_recipes
            
            # 合并备注
            if item.get("note") and item["note"] not in merged_ingredients[key].get("notes", []):
                merged_ingredients[key].setdefault("notes", []).append(item["note"])
        else:
            # 新项目
            merged_item = item.copy()
            merged_item["recipeIds"] = [item["recipeId"]] if item["recipeId"] else []
            merged_item["notes"] = [item["note"]] if item.get("note") else []
            merged_ingredients[key] = merged_item
    
    # 处理合并后的食材列表
    processed_items = []
    
    for key, item in merged_ingredients.items():
        # 删除临时字段
        if "recipeIds" in item:
            del item["recipeIds"]
        
        # 合并备注
        if "notes" in item:
            item["note"] = "; ".join(item["notes"])
            del item["notes"]
        
        processed_items.append(item)
    
    # 创建购物清单
    now = datetime.now()
    shopping_list_doc = {
        "planId": generate_data.planIds[0] if len(generate_data.planIds) == 1 else None,  # 如果只有一个计划，则关联
        "familyId": generate_data.familyId,
        "name": generate_data.name,
        "date": now,
        "items": processed_items,
        "totalCost": 0,  # 初始化总成本为0
        "status": ShoppingListStatus.PLANNING,
        "sharedWith": [],
        "createdAt": now,
        "updatedAt": now,
        "completedAt": None
    }
    
    # 插入购物清单
    result = await db.shopping_lists.insert_one(shopping_list_doc)
    
    # 如果只关联了一个菜单计划，更新其shoppingListId字段
    if len(generate_data.planIds) == 1:
        await db.menu_plans.update_one(
            {"_id": ObjectId(generate_data.planIds[0])},
            {"$set": {"shoppingListId": str(result.inserted_id)}}
        )
    
    # 获取创建的购物清单
    created_list = await db.shopping_lists.find_one({"_id": result.inserted_id})
    
    # 转换_id为字符串
    created_list["id"] = str(created_list.pop("_id"))
    
    return created_list


async def get_family_shopping_lists(
    params: ShoppingListListParams, 
    current_user: dict
) -> Tuple[List[dict], int]:
    """
    获取家庭的购物清单列表
    
    Args:
        params: 查询参数
        current_user: 当前用户信息
        
    Returns:
        购物清单列表和总数
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
        # 获取用户所有家庭的购物清单，以及用户有权访问的共享购物清单
        families = await db.families.find(
            {"members.userId": str(current_user["_id"])},
            {"_id": 1}
        ).to_list(length=100)
        
        family_ids = [str(family["_id"]) for family in families]
        
        if family_ids:
            query["$or"] = [
                {"familyId": {"$in": family_ids}},
                {"sharedWith.userId": str(current_user["_id"])}
            ]
        else:
            query["sharedWith.userId"] = str(current_user["_id"])
    
    # 状态过滤
    if params.status:
        query["status"] = {"$in": params.status}
    
    # 日期范围过滤
    date_filter = {}
    if params.startDate:
        date_filter["$gte"] = params.startDate
    if params.endDate:
        date_filter["$lte"] = params.endDate
    if date_filter:
        query["date"] = date_filter
    
    # 计算分页参数
    skip = (params.page - 1) * params.pageSize
    limit = params.pageSize
    
    # 查询总数
    total = await db.shopping_lists.count_documents(query)
    
    # 执行查询
    cursor = db.shopping_lists.find(query)
    cursor = cursor.sort("date", -1)  # 默认按日期降序排序
    cursor = cursor.skip(skip).limit(limit)
    
    # 获取结果
    lists = await cursor.to_list(length=limit)
    
    # 处理结果
    for shopping_list in lists:
        shopping_list["id"] = str(shopping_list.pop("_id"))
    
    return lists, total 
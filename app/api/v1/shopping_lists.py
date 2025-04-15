from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db
from app.db.mongodb import get_collection, SHOPPING_LISTS_COLLECTION
from app.models.shopping_list import (
    ShoppingListCreate, 
    ShoppingListResponse, 
    ShoppingListUpdate,
    ShoppingListItemBatchUpdate,
    ShoppingListGenerateRequest,
    ShoppingListStatus
)
from app.models.user import UserResponse


router = APIRouter()


@router.get("/", response_model=List[ShoppingListResponse], status_code=status.HTTP_200_OK)
async def get_shopping_lists(
    status: Optional[ShoppingListStatus] = None,
    family_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取当前用户的购物清单列表
    
    可选参数:
    - status: 筛选指定状态的购物清单
    - family_id: 筛选指定家庭的购物清单
    - limit: 分页大小
    - skip: 跳过记录数量
    """
    query = {}
    
    # 根据用户ID限制查询范围
    query["$or"] = [
        {"shared_with": current_user.id},
        {"creator_id": current_user.id}
    ]
    
    # 应用筛选条件
    if status:
        query["status"] = status
    
    if family_id:
        query["family_id"] = family_id
    
    collection = get_collection(SHOPPING_LISTS_COLLECTION)
    cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
    
    results = []
    async for doc in cursor:
        # 转换MongoDB _id为字符串ID
        doc["id"] = str(doc.pop("_id"))
        # 确保项目列表中的ID也被正确转换
        if "items" in doc:
            for item in doc["items"]:
                if "_id" in item:
                    item["id"] = str(item.pop("_id"))
        
        # 构建响应对象
        shopping_list = ShoppingListResponse(**doc)
        results.append(shopping_list)
    
    return results


@router.post("/", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
async def create_shopping_list(
    shopping_list: ShoppingListCreate,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    创建新的购物清单
    """
    # 准备数据库文档
    now = datetime.now()
    shopping_list_doc = shopping_list.dict()
    
    # 添加创建者和时间戳
    shopping_list_doc["creator_id"] = current_user.id
    shopping_list_doc["created_at"] = now
    shopping_list_doc["updated_at"] = now
    
    # 为每个物品生成ID
    for i, item in enumerate(shopping_list_doc.get("items", [])):
        item["_id"] = ObjectId()
    
    # 插入数据库
    collection = get_collection(SHOPPING_LISTS_COLLECTION)
    result = await collection.insert_one(shopping_list_doc)
    
    # 获取完整的文档
    created_document = await collection.find_one({"_id": result.inserted_id})
    
    # 准备响应
    created_document["id"] = str(created_document.pop("_id"))
    
    # 转换项目ID
    if "items" in created_document:
        for item in created_document["items"]:
            if "_id" in item:
                item["id"] = str(item.pop("_id"))
    
    return ShoppingListResponse(**created_document)


@router.get("/{shopping_list_id}", response_model=ShoppingListResponse)
async def get_shopping_list(
    shopping_list_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取特定购物清单的详情
    """
    try:
        object_id = ObjectId(shopping_list_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的购物清单ID格式"
        )
    
    collection = get_collection(SHOPPING_LISTS_COLLECTION)
    shopping_list = await collection.find_one({
        "_id": object_id,
        "$or": [
            {"shared_with": current_user.id},
            {"creator_id": current_user.id}
        ]
    })
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到购物清单或无权访问"
        )
    
    # 转换ID
    shopping_list["id"] = str(shopping_list.pop("_id"))
    
    # 转换项目ID
    if "items" in shopping_list:
        for item in shopping_list["items"]:
            if "_id" in item:
                item["id"] = str(item.pop("_id"))
    
    return ShoppingListResponse(**shopping_list)


@router.put("/{shopping_list_id}", response_model=ShoppingListResponse)
async def update_shopping_list(
    shopping_list_id: str,
    update_data: ShoppingListUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    更新购物清单的基本信息
    """
    try:
        object_id = ObjectId(shopping_list_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的购物清单ID格式"
        )
    
    # 转换为字典并移除None值
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    # 添加更新时间
    update_dict["updated_at"] = datetime.now()
    
    # 如果状态改为已完成，设置完成时间
    if update_data.status == ShoppingListStatus.COMPLETED:
        update_dict["completed_at"] = datetime.now()
    
    collection = get_collection(SHOPPING_LISTS_COLLECTION)
    
    # 先检查权限
    shopping_list = await collection.find_one({
        "_id": object_id,
        "$or": [
            {"shared_with": current_user.id},
            {"creator_id": current_user.id}
        ]
    })
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到购物清单或无权访问"
        )
    
    # 执行更新
    await collection.update_one(
        {"_id": object_id},
        {"$set": update_dict}
    )
    
    # 获取更新后的文档
    updated_doc = await collection.find_one({"_id": object_id})
    updated_doc["id"] = str(updated_doc.pop("_id"))
    
    # 转换项目ID
    if "items" in updated_doc:
        for item in updated_doc["items"]:
            if "_id" in item:
                item["id"] = str(item.pop("_id"))
    
    return ShoppingListResponse(**updated_doc)


@router.delete("/{shopping_list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    shopping_list_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    删除购物清单
    """
    try:
        object_id = ObjectId(shopping_list_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的购物清单ID格式"
        )
    
    collection = get_collection(SHOPPING_LISTS_COLLECTION)
    
    # 先检查权限 - 只有创建者可以删除
    shopping_list = await collection.find_one({
        "_id": object_id,
        "creator_id": current_user.id
    })
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到购物清单或无权删除"
        )
    
    await collection.delete_one({"_id": object_id})
    return None


@router.put("/{shopping_list_id}/items/batch", response_model=ShoppingListResponse)
async def update_items_batch(
    shopping_list_id: str,
    update_data: ShoppingListItemBatchUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    批量更新购物清单中的多个项目状态
    """
    try:
        list_id = ObjectId(shopping_list_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的购物清单ID格式"
        )
    
    # 将字符串ID转换为ObjectId
    item_object_ids = []
    for item_id in update_data.item_ids:
        try:
            item_object_ids.append(ObjectId(item_id))
        except:
            # 跳过无效ID
            continue
    
    if not item_object_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未提供有效的物品ID列表"
        )
    
    collection = get_collection(SHOPPING_LISTS_COLLECTION)
    
    # 检查权限
    shopping_list = await collection.find_one({
        "_id": list_id,
        "$or": [
            {"shared_with": current_user.id},
            {"creator_id": current_user.id}
        ]
    })
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到购物清单或无权访问"
        )
    
    # 更新所有指定的物品
    now = datetime.now()
    update_data_dict = {
        "is_purchased": update_data.is_purchased,
    }
    
    # 如果勾选，添加购买者信息和时间
    if update_data.is_purchased:
        update_data_dict["purchased_by"] = current_user.id
        update_data_dict["purchased_at"] = now
    
    # 更新时间戳
    await collection.update_one(
        {"_id": list_id},
        {"$set": {"updated_at": now}}
    )
    
    # 更新所有匹配的物品
    await collection.update_many(
        {
            "_id": list_id,
            "items._id": {"$in": item_object_ids}
        },
        {"$set": {f"items.$.{k}": v for k, v in update_data_dict.items()}}
    )
    
    # 获取更新后的完整文档
    updated_doc = await collection.find_one({"_id": list_id})
    updated_doc["id"] = str(updated_doc.pop("_id"))
    
    # 转换项目ID
    if "items" in updated_doc:
        for item in updated_doc["items"]:
            if "_id" in item:
                item["id"] = str(item.pop("_id"))
    
    return ShoppingListResponse(**updated_doc)


@router.post("/generate", response_model=ShoppingListResponse)
async def generate_shopping_list(
    request: ShoppingListGenerateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    基于菜单计划生成购物清单
    """
    # TODO: 实现从菜单计划生成购物清单的逻辑
    # 这将涉及:
    # 1. 获取所有指定的菜单计划
    # 2. 提取所有需要的食材
    # 3. 合并相同的食材并计算总量
    # 4. 创建新的购物清单
    
    # 临时实现
    shopping_list = ShoppingListCreate(
        name=request.name,
        family_id=request.family_id,
        items=[]
    )
    
    # 使用创建购物清单的接口逻辑
    return await create_shopping_list(shopping_list, current_user, db) 
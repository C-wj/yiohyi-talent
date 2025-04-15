from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from bson import ObjectId
from fastapi import HTTPException, status

from app.db.mongodb import get_database
from app.models.family import (
    FamilyCreate,
    FamilyUpdate,
    FamilyMember,
    FamilyMemberAdd,
    FamilyMemberUpdate,
    FamilyInvitation,
    FamilyInvitationCreate,
    FamilyMemberRole
)


async def create_family(family_data: FamilyCreate, current_user: dict) -> dict:
    """
    创建新家庭
    
    Args:
        family_data: 家庭创建数据
        current_user: 当前用户信息
        
    Returns:
        创建的家庭信息
    """
    db = await get_database()
    
    # 创建家庭创建者作为第一个成员
    creator = FamilyMember(
        userId=str(current_user["_id"]),
        nickname=current_user["profile"]["nickname"],
        avatar=current_user["profile"].get("avatar"),
        role=FamilyMemberRole.OWNER,
        joinedAt=datetime.now()
    )
    
    # 构建家庭文档
    now = datetime.now()
    family_doc = {
        "name": family_data.name,
        "avatar": family_data.avatar,
        "creator": str(current_user["_id"]),
        "members": [creator.dict()],
        "settings": family_data.settings.dict() if family_data.settings else {},
        "invitations": [],
        "createdAt": now,
        "updatedAt": now
    }
    
    # 插入家庭文档
    result = await db.families.insert_one(family_doc)
    
    # 获取创建的家庭
    created_family = await db.families.find_one({"_id": result.inserted_id})
    
    # 转换_id为字符串
    created_family["id"] = str(created_family.pop("_id"))
    
    return created_family


async def get_family_by_id(family_id: str, current_user: dict) -> Optional[dict]:
    """
    根据ID获取家庭详情
    
    Args:
        family_id: 家庭ID
        current_user: 当前用户信息
        
    Returns:
        家庭详情或None(如果不存在或无权访问)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        family_object_id = ObjectId(family_id)
    except:
        # ID格式无效
        return None
    
    # 查询家庭
    family = await db.families.find_one({"_id": family_object_id})
    
    if not family:
        return None
    
    # 检查访问权限(仅家庭成员可以访问)
    is_member = False
    for member in family.get("members", []):
        if str(member.get("userId")) == str(current_user["_id"]):
            is_member = True
            break
    
    if not is_member and "admin" not in current_user.get("roles", []):
        return None
    
    # 转换_id为字符串
    family["id"] = str(family.pop("_id"))
    
    return family


async def update_family(family_id: str, family_data: FamilyUpdate, current_user: dict) -> Optional[dict]:
    """
    更新家庭信息
    
    Args:
        family_id: 家庭ID
        family_data: 更新数据
        current_user: 当前用户信息
        
    Returns:
        更新后的家庭或None(如果不存在或无权限)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        family_object_id = ObjectId(family_id)
    except:
        # ID格式无效
        return None
    
    # 查询家庭
    family = await db.families.find_one({"_id": family_object_id})
    
    if not family:
        return None
    
    # 检查更新权限(只有创建者和管理员可以更新)
    has_permission = False
    if str(family["creator"]) == str(current_user["_id"]):
        has_permission = True
    else:
        for member in family.get("members", []):
            if (str(member.get("userId")) == str(current_user["_id"]) and 
                member.get("role") in [FamilyMemberRole.OWNER, FamilyMemberRole.ADMIN]):
                has_permission = True
                break
    
    if not has_permission and "admin" not in current_user.get("roles", []):
        return None
    
    # 构建更新文档
    update_doc = {}
    update_fields = family_data.dict(exclude_unset=True)
    
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
    await db.families.update_one(
        {"_id": family_object_id},
        {"$set": update_doc}
    )
    
    # 获取更新后的家庭
    updated_family = await db.families.find_one({"_id": family_object_id})
    
    # 转换_id为字符串
    updated_family["id"] = str(updated_family.pop("_id"))
    
    return updated_family


async def add_family_member(family_id: str, member_data: FamilyMemberAdd, current_user: dict) -> Optional[dict]:
    """
    添加家庭成员
    
    Args:
        family_id: 家庭ID
        member_data: 成员数据
        current_user: 当前用户信息
        
    Returns:
        更新后的家庭或None(如果不存在或无权限)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        family_object_id = ObjectId(family_id)
    except:
        # ID格式无效
        return None
    
    # 查询家庭
    family = await db.families.find_one({"_id": family_object_id})
    
    if not family:
        return None
    
    # 检查权限(只有创建者和管理员可以添加成员)
    has_permission = False
    if str(family["creator"]) == str(current_user["_id"]):
        has_permission = True
    else:
        for member in family.get("members", []):
            if (str(member.get("userId")) == str(current_user["_id"]) and 
                member.get("role") in [FamilyMemberRole.OWNER, FamilyMemberRole.ADMIN]):
                has_permission = True
                break
    
    if not has_permission and "admin" not in current_user.get("roles", []):
        return None
    
    # 检查用户是否已是家庭成员
    for member in family.get("members", []):
        if str(member.get("userId")) == str(member_data.userId):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户已是家庭成员"
            )
    
    # 创建新成员
    new_member = FamilyMember(
        userId=member_data.userId,
        nickname=member_data.nickname,
        avatar=member_data.avatar,
        role=member_data.role,
        joinedAt=datetime.now()
    )
    
    # 添加成员到家庭
    await db.families.update_one(
        {"_id": family_object_id},
        {
            "$push": {"members": new_member.dict()},
            "$set": {"updatedAt": datetime.now()}
        }
    )
    
    # 获取更新后的家庭
    updated_family = await db.families.find_one({"_id": family_object_id})
    
    # 转换_id为字符串
    updated_family["id"] = str(updated_family.pop("_id"))
    
    return updated_family


async def update_family_member(
    family_id: str, 
    member_id: str, 
    member_data: FamilyMemberUpdate, 
    current_user: dict
) -> Optional[dict]:
    """
    更新家庭成员信息
    
    Args:
        family_id: 家庭ID
        member_id: 成员用户ID
        member_data: 更新数据
        current_user: 当前用户信息
        
    Returns:
        更新后的家庭或None(如果不存在或无权限)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        family_object_id = ObjectId(family_id)
    except:
        # ID格式无效
        return None
    
    # 查询家庭
    family = await db.families.find_one({"_id": family_object_id})
    
    if not family:
        return None
    
    # 检查权限
    has_permission = False
    is_self_update = str(member_id) == str(current_user["_id"])
    
    if str(family["creator"]) == str(current_user["_id"]):
        # 创建者可以更新任何成员
        has_permission = True
    elif is_self_update:
        # 自己可以更新自己的部分信息(昵称和头像)
        if member_data.role is not None:
            # 不允许自己修改自己的角色
            member_data.role = None
        has_permission = True
    else:
        # 管理员可以更新普通成员
        current_role = None
        member_role = None
        
        # 获取当前用户和目标成员的角色
        for member in family.get("members", []):
            if str(member.get("userId")) == str(current_user["_id"]):
                current_role = member.get("role")
            elif str(member.get("userId")) == str(member_id):
                member_role = member.get("role")
        
        if (current_role in [FamilyMemberRole.OWNER, FamilyMemberRole.ADMIN] and 
            (member_role == FamilyMemberRole.MEMBER or 
             (member_role == FamilyMemberRole.ADMIN and current_role == FamilyMemberRole.OWNER))):
            has_permission = True
    
    if not has_permission and "admin" not in current_user.get("roles", []):
        return None
    
    # 查找成员在列表中的索引
    member_index = None
    for i, member in enumerate(family.get("members", [])):
        if str(member.get("userId")) == str(member_id):
            member_index = i
            break
    
    if member_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成员不存在"
        )
    
    # 构建更新操作
    update_operations = {}
    update_fields = member_data.dict(exclude_unset=True)
    
    for field, value in update_fields.items():
        if value is not None:
            update_operations[f"members.{member_index}.{field}"] = value
    
    # 添加更新时间
    update_operations["updatedAt"] = datetime.now()
    
    # 执行更新
    await db.families.update_one(
        {"_id": family_object_id},
        {"$set": update_operations}
    )
    
    # 获取更新后的家庭
    updated_family = await db.families.find_one({"_id": family_object_id})
    
    # 转换_id为字符串
    updated_family["id"] = str(updated_family.pop("_id"))
    
    return updated_family


async def remove_family_member(family_id: str, member_id: str, current_user: dict) -> Optional[dict]:
    """
    移除家庭成员
    
    Args:
        family_id: 家庭ID
        member_id: 成员用户ID
        current_user: 当前用户信息
        
    Returns:
        更新后的家庭或None(如果不存在或无权限)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        family_object_id = ObjectId(family_id)
    except:
        # ID格式无效
        return None
    
    # 查询家庭
    family = await db.families.find_one({"_id": family_object_id})
    
    if not family:
        return None
    
    # 检查权限
    has_permission = False
    is_self_remove = str(member_id) == str(current_user["_id"])
    
    if str(family["creator"]) == str(current_user["_id"]):
        # 创建者可以移除任何成员(除了自己)
        if not is_self_remove:
            has_permission = True
    elif is_self_remove:
        # 自己可以退出家庭
        has_permission = True
    else:
        # 管理员可以移除普通成员
        current_role = None
        member_role = None
        
        # 获取当前用户和目标成员的角色
        for member in family.get("members", []):
            if str(member.get("userId")) == str(current_user["_id"]):
                current_role = member.get("role")
            elif str(member.get("userId")) == str(member_id):
                member_role = member.get("role")
        
        if (current_role in [FamilyMemberRole.OWNER, FamilyMemberRole.ADMIN] and 
            (member_role == FamilyMemberRole.MEMBER or 
             (member_role == FamilyMemberRole.ADMIN and current_role == FamilyMemberRole.OWNER))):
            has_permission = True
    
    if not has_permission and "admin" not in current_user.get("roles", []):
        return None
    
    # 检查是否是创建者试图退出
    if is_self_remove and str(family["creator"]) == str(current_user["_id"]):
        # 如果家庭还有其他成员，需要转移所有权
        if len(family.get("members", [])) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建者在退出前需要转移家庭所有权"
            )
        # 如果家庭只有创建者一人，则可以删除整个家庭
        else:
            await db.families.delete_one({"_id": family_object_id})
            return {"message": "家庭已删除"}
    
    # 移除成员
    await db.families.update_one(
        {"_id": family_object_id},
        {
            "$pull": {"members": {"userId": member_id}},
            "$set": {"updatedAt": datetime.now()}
        }
    )
    
    # 获取更新后的家庭
    updated_family = await db.families.find_one({"_id": family_object_id})
    
    # 转换_id为字符串
    updated_family["id"] = str(updated_family.pop("_id"))
    
    return updated_family


async def create_family_invitation(family_id: str, invitation_data: FamilyInvitationCreate, current_user: dict) -> Optional[dict]:
    """
    创建家庭邀请码
    
    Args:
        family_id: 家庭ID
        invitation_data: 邀请数据
        current_user: 当前用户信息
        
    Returns:
        创建的邀请信息或None(如果不存在或无权限)
    """
    db = await get_database()
    
    try:
        # 转换字符串ID为ObjectId
        family_object_id = ObjectId(family_id)
    except:
        # ID格式无效
        return None
    
    # 查询家庭
    family = await db.families.find_one({"_id": family_object_id})
    
    if not family:
        return None
    
    # 检查权限(只有创建者和管理员可以创建邀请)
    has_permission = False
    if str(family["creator"]) == str(current_user["_id"]):
        has_permission = True
    else:
        for member in family.get("members", []):
            if (str(member.get("userId")) == str(current_user["_id"]) and 
                member.get("role") in [FamilyMemberRole.OWNER, FamilyMemberRole.ADMIN]):
                has_permission = True
                break
    
    if not has_permission and "admin" not in current_user.get("roles", []):
        return None
    
    # 创建邀请
    invitation = FamilyInvitation(
        createdBy=str(current_user["_id"]),
        expiresAt=datetime.now() + timedelta(days=invitation_data.expiresIn)
    )
    
    # 添加邀请到家庭
    await db.families.update_one(
        {"_id": family_object_id},
        {
            "$push": {"invitations": invitation.dict()},
            "$set": {"updatedAt": datetime.now()}
        }
    )
    
    # 构建邀请链接
    invitation_url = f"/families/join?code={invitation.code}"
    
    return {
        "code": invitation.code,
        "expiresAt": invitation.expiresAt,
        "url": invitation_url
    }


async def join_family_with_invitation(invitation_code: str, current_user: dict) -> Optional[dict]:
    """
    使用邀请码加入家庭
    
    Args:
        invitation_code: 邀请码
        current_user: 当前用户信息
        
    Returns:
        加入的家庭信息或None(如果邀请无效)
    """
    db = await get_database()
    
    # 查询包含此邀请码的家庭
    family = await db.families.find_one({"invitations.code": invitation_code})
    
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请码无效"
        )
    
    # 找到对应的邀请
    invitation = None
    invitation_index = None
    for i, inv in enumerate(family.get("invitations", [])):
        if inv["code"] == invitation_code:
            invitation = inv
            invitation_index = i
            break
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请码无效"
        )
    
    # 检查邀请是否过期
    if invitation.get("expiresAt") < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请码已过期"
        )
    
    # 检查邀请是否已使用
    if invitation.get("isUsed", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请码已被使用"
        )
    
    # 检查用户是否已是家庭成员
    for member in family.get("members", []):
        if str(member.get("userId")) == str(current_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已是该家庭成员"
            )
    
    # 创建新成员
    new_member = FamilyMember(
        userId=str(current_user["_id"]),
        nickname=current_user["profile"]["nickname"],
        avatar=current_user["profile"].get("avatar"),
        role=FamilyMemberRole.MEMBER,
        joinedAt=datetime.now()
    )
    
    # 更新邀请状态
    await db.families.update_one(
        {"_id": family["_id"], "invitations.code": invitation_code},
        {
            "$set": {
                f"invitations.{invitation_index}.isUsed": True,
                f"invitations.{invitation_index}.usedBy": str(current_user["_id"]),
                f"invitations.{invitation_index}.usedAt": datetime.now()
            }
        }
    )
    
    # 添加成员到家庭
    await db.families.update_one(
        {"_id": family["_id"]},
        {
            "$push": {"members": new_member.dict()},
            "$set": {"updatedAt": datetime.now()}
        }
    )
    
    # 获取更新后的家庭
    updated_family = await db.families.find_one({"_id": family["_id"]})
    
    # 转换_id为字符串
    updated_family["id"] = str(updated_family.pop("_id"))
    
    return updated_family


async def get_user_families(current_user: dict) -> List[dict]:
    """
    获取用户所有家庭
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        用户所属的家庭列表
    """
    db = await get_database()
    
    # 查询用户所属的家庭
    cursor = db.families.find({"members.userId": str(current_user["_id"])})
    
    # 获取结果
    families = await cursor.to_list(length=100)
    
    # 处理结果
    for family in families:
        family["id"] = str(family.pop("_id"))
    
    return families 
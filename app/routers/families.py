from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional

from app.models.family import (
    FamilyCreate, 
    FamilyUpdate, 
    FamilyResponse, 
    FamilyMemberAdd,
    FamilyMemberUpdate,
    FamilyInvitationCreate,
    FamilyInvitationResponse
)
from app.services import family as family_service
from app.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/families",
    tags=["families"]
)


@router.post("", response_model=FamilyResponse)
async def create_family(
    family_data: FamilyCreate, 
    current_user: dict = Depends(get_current_user)
):
    """创建新家庭"""
    return await family_service.create_family(family_data, current_user)


@router.get("", response_model=List[FamilyResponse])
async def get_user_families(
    current_user: dict = Depends(get_current_user)
):
    """获取当前用户的所有家庭"""
    return await family_service.get_user_families(current_user)


@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(
    family_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取家庭详情"""
    family = await family_service.get_family_by_id(family_id, current_user)
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="家庭不存在或无权访问"
        )
    return family


@router.put("/{family_id}", response_model=FamilyResponse)
async def update_family(
    family_id: str,
    family_data: FamilyUpdate,
    current_user: dict = Depends(get_current_user)
):
    """更新家庭信息"""
    updated_family = await family_service.update_family(family_id, family_data, current_user)
    if not updated_family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="家庭不存在或无权更新"
        )
    return updated_family


@router.post("/{family_id}/members", response_model=FamilyResponse)
async def add_family_member(
    family_id: str,
    member_data: FamilyMemberAdd,
    current_user: dict = Depends(get_current_user)
):
    """添加家庭成员"""
    updated_family = await family_service.add_family_member(family_id, member_data, current_user)
    if not updated_family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="家庭不存在或无权添加成员"
        )
    return updated_family


@router.put("/{family_id}/members/{member_id}", response_model=FamilyResponse)
async def update_family_member(
    family_id: str,
    member_id: str,
    member_data: FamilyMemberUpdate,
    current_user: dict = Depends(get_current_user)
):
    """更新家庭成员信息"""
    updated_family = await family_service.update_family_member(family_id, member_id, member_data, current_user)
    if not updated_family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="家庭不存在或无权更新成员"
        )
    return updated_family


@router.delete("/{family_id}/members/{member_id}", response_model=FamilyResponse)
async def remove_family_member(
    family_id: str,
    member_id: str,
    current_user: dict = Depends(get_current_user)
):
    """移除家庭成员"""
    result = await family_service.remove_family_member(family_id, member_id, current_user)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="家庭不存在或无权移除成员"
        )
    return result


@router.post("/{family_id}/invitations", response_model=FamilyInvitationResponse)
async def create_invitation(
    family_id: str,
    invitation_data: FamilyInvitationCreate,
    current_user: dict = Depends(get_current_user)
):
    """创建家庭邀请码"""
    invitation = await family_service.create_family_invitation(family_id, invitation_data, current_user)
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="家庭不存在或无权创建邀请"
        )
    return invitation


@router.post("/join", response_model=FamilyResponse)
async def join_family(
    invitation_code: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """通过邀请码加入家庭"""
    family = await family_service.join_family_with_invitation(invitation_code, current_user)
    return family 
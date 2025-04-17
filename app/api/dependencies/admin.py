"""
管理员权限验证依赖
"""
from fastapi import Depends, HTTPException, status
from typing import Optional, List

from app.api.dependencies.auth import get_current_user
from app.models.user import UserRole, UserResponse


async def get_current_admin(current_user: UserResponse = Depends(get_current_user)):
    """
    验证当前用户是否具有管理员权限
    
    依赖于get_current_user，先验证用户登录，再验证管理员权限
    """
    # 检查用户是否存在角色列表
    if not hasattr(current_user, "roles"):
        # 兼容当前UserResponse模型可能没有roles字段
        # 如果模型没有roles字段，默认没有管理员权限
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    
    # 检查是否具有管理员或超级管理员角色
    if UserRole.ADMIN.value not in current_user.roles and UserRole.SUPER_ADMIN.value not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    
    return current_user


async def get_current_super_admin(current_user: UserResponse = Depends(get_current_user)):
    """
    验证当前用户是否具有超级管理员权限
    
    依赖于get_current_user，先验证用户登录，再验证超级管理员权限
    """
    # 检查用户是否存在角色列表
    if not hasattr(current_user, "roles"):
        # 兼容当前UserResponse模型可能没有roles字段
        # 如果模型没有roles字段，默认没有超级管理员权限
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级管理员权限"
        )
    
    # 检查是否具有超级管理员角色
    if UserRole.SUPER_ADMIN.value not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级管理员权限"
        )
    
    return current_user 
"""
权限验证中间件
用于检查用户是否有访问特定资源的权限
"""

import logging
from typing import List, Optional, Callable, Any
from functools import wraps

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.jwt import verify_token
from app.services.rbac_service import UserRoleService
from app.core.response import unauthorized_response

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self):
        self.user_role_service = UserRoleService()
    
    async def check_permission(
        self,
        user_id: str,
        permission_code: str,
        resource_id: Optional[str] = None
    ) -> bool:
        """
        检查用户是否有指定权限
        
        Args:
            user_id: 用户ID
            permission_code: 权限代码
            resource_id: 资源ID（可选，用于资源级权限控制）
        
        Returns:
            bool: 是否有权限
        """
        try:
            # 检查用户权限
            has_permission = await self.user_role_service.check_user_permission(
                user_id, permission_code
            )
            
            if not has_permission:
                logger.warning(f"用户 {user_id} 没有权限 {permission_code}")
                return False
            
            # TODO: 如果需要资源级权限控制，可以在这里添加额外的检查逻辑
            # 例如：检查用户是否有权限访问特定的资源实例
            
            return True
            
        except Exception as e:
            logger.error(f"权限检查失败: {str(e)}")
            return False
    
    async def check_multiple_permissions(
        self,
        user_id: str,
        permission_codes: List[str],
        require_all: bool = True
    ) -> bool:
        """
        检查用户是否有多个权限
        
        Args:
            user_id: 用户ID
            permission_codes: 权限代码列表
            require_all: 是否需要所有权限（True）还是任一权限（False）
        
        Returns:
            bool: 是否有权限
        """
        try:
            results = []
            for permission_code in permission_codes:
                has_permission = await self.check_permission(user_id, permission_code)
                results.append(has_permission)
            
            if require_all:
                return all(results)
            else:
                return any(results)
                
        except Exception as e:
            logger.error(f"多权限检查失败: {str(e)}")
            return False


# 全局权限检查器实例
permission_checker = PermissionChecker()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    获取当前用户信息
    
    Args:
        credentials: HTTP Bearer token
    
    Returns:
        dict: 用户信息
    
    Raises:
        HTTPException: 认证失败时抛出异常
    """
    try:
        # 验证token
        payload = verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的访问令牌"
            )
        
        return payload
        
    except Exception as e:
        logger.error(f"用户认证失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败"
        )


def require_permission(permission_code: str):
    """
    权限装饰器 - 要求特定权限
    
    Args:
        permission_code: 权限代码
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取current_user
            current_user = kwargs.get('current_user')
            if not current_user:
                # 如果没有current_user，尝试从依赖注入中获取
                for arg in args:
                    if isinstance(arg, dict) and 'user_id' in arg:
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未找到用户信息"
                )
            
            user_id = current_user.get('user_id')
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的用户信息"
                )
            
            # 检查权限
            has_permission = await permission_checker.check_permission(
                user_id, permission_code
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"没有权限执行此操作 ({permission_code})"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_any_permission(permission_codes: List[str]):
    """
    权限装饰器 - 要求任一权限
    
    Args:
        permission_codes: 权限代码列表
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                for arg in args:
                    if isinstance(arg, dict) and 'user_id' in arg:
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未找到用户信息"
                )
            
            user_id = current_user.get('user_id')
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的用户信息"
                )
            
            # 检查是否有任一权限
            has_permission = await permission_checker.check_multiple_permissions(
                user_id, permission_codes, require_all=False
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"没有权限执行此操作 (需要以下权限之一: {', '.join(permission_codes)})"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_all_permissions(permission_codes: List[str]):
    """
    权限装饰器 - 要求所有权限
    
    Args:
        permission_codes: 权限代码列表
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                for arg in args:
                    if isinstance(arg, dict) and 'user_id' in arg:
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未找到用户信息"
                )
            
            user_id = current_user.get('user_id')
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的用户信息"
                )
            
            # 检查是否有所有权限
            has_permission = await permission_checker.check_multiple_permissions(
                user_id, permission_codes, require_all=True
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"没有权限执行此操作 (需要以下所有权限: {', '.join(permission_codes)})"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class PermissionDependency:
    """权限依赖类 - 用于FastAPI的Depends"""
    
    def __init__(self, permission_code: str):
        self.permission_code = permission_code
    
    async def __call__(self, current_user: dict = Depends(get_current_user)):
        """
        检查权限的依赖函数
        
        Args:
            current_user: 当前用户信息
        
        Returns:
            dict: 用户信息（如果有权限）
        
        Raises:
            HTTPException: 没有权限时抛出异常
        """
        user_id = current_user.get('user_id')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的用户信息"
            )
        
        # 检查权限
        has_permission = await permission_checker.check_permission(
            user_id, self.permission_code
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"没有权限执行此操作 ({self.permission_code})"
            )
        
        return current_user


def permission_required(permission_code: str):
    """
    创建权限依赖
    
    Args:
        permission_code: 权限代码
    
    Returns:
        PermissionDependency: 权限依赖实例
    """
    return PermissionDependency(permission_code)


# 常用权限依赖
class CommonPermissions:
    """常用权限依赖"""
    
    # 角色管理权限
    role_create = permission_required("role:create")
    role_read = permission_required("role:read")
    role_update = permission_required("role:update")
    role_delete = permission_required("role:delete")
    
    # 权限管理权限
    permission_create = permission_required("permission:create")
    permission_read = permission_required("permission:read")
    permission_update = permission_required("permission:update")
    permission_delete = permission_required("permission:delete")
    
    # 菜单管理权限
    menu_create = permission_required("menu:create")
    menu_read = permission_required("menu:read")
    menu_update = permission_required("menu:update")
    menu_delete = permission_required("menu:delete")
    
    # 用户管理权限
    user_create = permission_required("user:create")
    user_read = permission_required("user:read")
    user_update = permission_required("user:update")
    user_delete = permission_required("user:delete")
    
    # 用户角色管理权限
    user_role_assign = permission_required("user_role:assign")
    user_role_read = permission_required("user_role:read")
    user_permission_read = permission_required("user_permission:read")
    
    # 系统配置权限
    system_config = permission_required("system:config")
    dict_manage = permission_required("dict:manage")
    notice_manage = permission_required("notice:manage")
    
    # 内容管理权限
    recipe_manage = permission_required("recipe:manage")
    order_manage = permission_required("order:manage")
    
    # 统计分析权限
    stats_view = permission_required("stats:view")
    report_export = permission_required("report:export") 
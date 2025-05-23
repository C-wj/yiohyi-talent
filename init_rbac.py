#!/usr/bin/env python3
"""
初始化RBAC权限脚本：
1. 为指定用户分配超级管理员角色
2. 测试权限是否生效
"""

import os
import asyncio
from bson.objectid import ObjectId
from app.db.mongodb import connect_to_mongo, get_database
from app.models.rbac import USER_ROLES_COLLECTION, ROLES_COLLECTION

async def init_rbac():
    """初始化RBAC权限"""
    try:
        # 设置环境
        os.environ['APP_ENV'] = 'development'
        
        # 连接数据库
        await connect_to_mongo()
        db = get_database()
        
        # 用户ID
        user_id = "682d6fa6a234817b168c9be5"
        print(f"为用户 {user_id} 分配超级管理员角色...")
        
        # 获取超级管理员角色ID
        role_collection = db[ROLES_COLLECTION]
        super_admin_role = await role_collection.find_one({"code": "super_admin"})
        
        if not super_admin_role:
            print("错误: 找不到超级管理员角色!")
            return
        
        super_admin_id = str(super_admin_role["_id"])
        print(f"超级管理员角色ID: {super_admin_id}")
        
        # 检查用户角色是否已存在
        user_role_collection = db[USER_ROLES_COLLECTION]
        existing_role = await user_role_collection.find_one({
            "user_id": user_id,
            "role_id": super_admin_id
        })
        
        if existing_role:
            print("用户已有超级管理员角色，更新角色状态为激活...")
            await user_role_collection.update_one(
                {"_id": existing_role["_id"]},
                {"$set": {"is_active": True}}
            )
        else:
            print("创建新的用户角色关联...")
            user_role_data = {
                "user_id": user_id,
                "role_id": super_admin_id,
                "assigned_by": user_id,  # 自己分配给自己
                "is_active": True,
                "created_at": datetime.datetime.utcnow(),
                "updated_at": datetime.datetime.utcnow()
            }
            await user_role_collection.insert_one(user_role_data)
        
        print("用户角色分配成功！")
        
        # 验证分配结果
        from app.services.rbac_service import UserRoleService
        
        print("\n验证用户角色和权限...")
        roles = await UserRoleService.get_user_roles(user_id)
        print(f"用户角色数量: {len(roles)}")
        
        for role in roles:
            print(f"角色: {role['name']} ({role['code']})")
            print(f"权限数量: {len(role.get('permissions', []))}")
        
        permissions = await UserRoleService.get_user_permissions(user_id)
        print(f"\n用户权限数量: {len(permissions)}")
        print(f"前10个权限: {permissions[:10]}")
        
        # 检查关键权限
        key_permissions = ["role:read", "menu:read", "permission:read"]
        for perm in key_permissions:
            has_perm = await UserRoleService.check_permission(user_id, perm)
            print(f"权限 {perm}: {'✓' if has_perm else '✗'}")
            
    except Exception as e:
        print(f"初始化RBAC权限失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import datetime  # 导入datetime模块，用于创建时间戳
    asyncio.run(init_rbac()) 
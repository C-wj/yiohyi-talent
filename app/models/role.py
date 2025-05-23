from datetime import datetime
from bson import ObjectId
from app.utils.mongodb_utils import get_db, serialize_document

class Role:
    """角色模型"""
    
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.roles
        
    def create_role(self, data):
        """创建角色"""
        role = {
            "name": data.get("name"),
            "code": data.get("code"),  # 角色代码：super_admin, admin, member, user
            "description": data.get("description"),
            "permissions": data.get("permissions", []),  # 权限ID列表
            "menus": data.get("menus", []),  # 菜单ID列表
            "status": data.get("status", 1),  # 1: 启用, 0: 禁用
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = self.collection.insert_one(role)
        role["_id"] = result.inserted_id
        return serialize_document(role)
    
    def get_role_by_code(self, code):
        """根据角色代码获取角色"""
        role = self.collection.find_one({"code": code})
        return serialize_document(role) if role else None
    
    def get_all_roles(self):
        """获取所有角色"""
        roles = list(self.collection.find())
        return [serialize_document(role) for role in roles]
    
    def update_role(self, role_id, data):
        """更新角色"""
        data["updated_at"] = datetime.utcnow()
        result = self.collection.update_one(
            {"_id": ObjectId(role_id)},
            {"$set": data}
        )
        return result.modified_count > 0
    
    def delete_role(self, role_id):
        """删除角色"""
        result = self.collection.delete_one({"_id": ObjectId(role_id)})
        return result.deleted_count > 0
    
    def init_default_roles(self):
        """初始化默认角色"""
        default_roles = [
            {
                "name": "超级管理员",
                "code": "super_admin",
                "description": "拥有系统所有权限",
                "permissions": ["*"],  # 所有权限
                "status": 1
            },
            {
                "name": "管理员",
                "code": "admin",
                "description": "拥有部分管理权限",
                "permissions": [],
                "status": 1
            },
            {
                "name": "会员",
                "code": "member",
                "description": "付费会员，享有特殊权限",
                "permissions": [],
                "status": 1
            },
            {
                "name": "普通用户",
                "code": "user",
                "description": "普通注册用户",
                "permissions": [],
                "status": 1
            }
        ]
        
        for role_data in default_roles:
            if not self.get_role_by_code(role_data["code"]):
                self.create_role(role_data) 
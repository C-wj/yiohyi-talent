from datetime import datetime
from bson import ObjectId
from app.utils.mongodb_utils import get_db, serialize_document

class Announcement:
    """公告模型"""
    
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.announcements
        
    def create_announcement(self, data):
        """创建公告"""
        announcement = {
            "title": data.get("title"),
            "content": data.get("content"),
            "type": data.get("type", "notice"),  # notice: 通知, announcement: 公告
            "level": data.get("level", "info"),  # info, warning, error
            "target_roles": data.get("target_roles", []),  # 目标角色
            "start_time": data.get("start_time"),
            "end_time": data.get("end_time"),
            "status": data.get("status", 1),
            "created_by": data.get("created_by"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = self.collection.insert_one(announcement)
        announcement["_id"] = result.inserted_id
        return serialize_document(announcement)
    
    def get_active_announcements(self, role_code=None):
        """获取有效公告"""
        now = datetime.utcnow()
        query = {
            "status": 1,
            "$or": [
                {"start_time": {"$lte": now}, "end_time": {"$gte": now}},
                {"start_time": None, "end_time": None}
            ]
        }
        
        if role_code and role_code != "super_admin":
            query["$or"].append({"target_roles": []})
            query["$or"].append({"target_roles": role_code})
        
        announcements = list(self.collection.find(query).sort("created_at", -1))
        return [serialize_document(a) for a in announcements] 
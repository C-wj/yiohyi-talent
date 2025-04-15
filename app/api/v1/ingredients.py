from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_ingredients():
    """获取食材列表（示例）"""
    return {"message": "食材路由创建成功"}

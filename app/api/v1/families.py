from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_families():
    """获取家庭列表（示例）"""
    return {"message": "家庭路由创建成功"}

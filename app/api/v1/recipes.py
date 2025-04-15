from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_recipes():
    """获取菜谱列表（示例）"""
    return {"message": "菜谱路由创建成功"}

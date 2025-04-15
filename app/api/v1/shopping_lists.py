from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_shopping_lists():
    """获取购物清单列表（示例）"""
    return {"message": "购物清单路由创建成功"}

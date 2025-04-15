from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    """
    获取用户列表（示例）
    """
    return {"message": "用户路由创建成功"}

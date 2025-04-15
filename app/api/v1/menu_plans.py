from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_menu_plans():
    """获取菜单计划列表（示例）"""
    return {"message": "菜单计划路由创建成功"}

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_uploads():
    """获取上传文件列表（示例）"""
    return {"message": "文件上传路由创建成功"}

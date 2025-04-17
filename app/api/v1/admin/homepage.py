"""
管理员首页内容管理API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status

from app.api.dependencies.admin import get_current_admin
from app.models.homepage import (
    ContentType,
    ContentStatus,
    HomeContent,
    SwiperCreate,
    SwiperUpdate,
    CardCreate,
    CardUpdate,
    ContentFilter,
    HomeContentResponse
)
from app.models.user import UserResponse
from app.services.homepage import (
    get_content_by_id,
    create_content,
    update_content,
    delete_content,
    list_contents,
    count_contents,
    create_swiper,
    create_card
)

router = APIRouter()


@router.get("/contents", response_model=List[HomeContentResponse])
async def list_homepage_contents(
    content_type: Optional[str] = Query(None, description="内容类型"),
    status: Optional[str] = Query(None, description="内容状态"),
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(20, description="返回的记录数"),
    current_admin: UserResponse = Depends(get_current_admin)
):
    """
    获取首页内容列表
    
    需要管理员权限
    """
    contents = await list_contents(content_type, status, skip, limit)
    return contents


@router.get("/contents/{content_id}", response_model=HomeContentResponse)
async def get_homepage_content(
    content_id: str = Path(..., description="内容ID"),
    current_admin: UserResponse = Depends(get_current_admin)
):
    """
    获取指定ID的首页内容
    
    需要管理员权限
    """
    content = await get_content_by_id(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"内容 {content_id} 不存在"
        )
    return content


@router.post("/contents/swipers", response_model=HomeContentResponse)
async def create_homepage_swiper(
    swiper_data: SwiperCreate,
    current_admin: UserResponse = Depends(get_current_admin)
):
    """
    创建首页轮播图
    
    需要管理员权限
    """
    created_swiper = await create_swiper(swiper_data, str(current_admin.id))
    return created_swiper


@router.post("/contents/featured", response_model=HomeContentResponse)
async def create_homepage_featured(
    card_data: CardCreate,
    current_admin: UserResponse = Depends(get_current_admin)
):
    """
    创建首页精选推荐
    
    需要管理员权限
    """
    created_card = await create_card(card_data, ContentType.FEATURED, str(current_admin.id))
    return created_card


@router.post("/contents/popular", response_model=HomeContentResponse)
async def create_homepage_popular(
    card_data: CardCreate,
    current_admin: UserResponse = Depends(get_current_admin)
):
    """
    创建首页热门菜谱
    
    需要管理员权限
    """
    created_card = await create_card(card_data, ContentType.POPULAR, str(current_admin.id))
    return created_card


@router.put("/contents/{content_id}", response_model=HomeContentResponse)
async def update_homepage_content(
    content_id: str,
    update_data: dict,
    current_admin: UserResponse = Depends(get_current_admin)
):
    """
    更新首页内容
    
    需要管理员权限
    """
    # 检查内容是否存在
    content = await get_content_by_id(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"内容 {content_id} 不存在"
        )
    
    # 更新内容
    updated_content = await update_content(content_id, update_data, str(current_admin.id))
    return updated_content


@router.delete("/contents/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_homepage_content(
    content_id: str,
    current_admin: UserResponse = Depends(get_current_admin)
):
    """
    删除首页内容
    
    需要管理员权限
    """
    # 检查内容是否存在
    content = await get_content_by_id(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"内容 {content_id} 不存在"
        )
    
    # 删除内容
    result = await delete_content(content_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除内容失败"
        )
    
    return None 
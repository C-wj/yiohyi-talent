from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional

from app.api.dependencies import get_current_user
from app.models.recipe import RecipeCreate, RecipeUpdate, RecipeResponse, RecipeSearchParams
from app.models.comment import CommentCreate, CommentResponse, CommentListResponse
from app.services.recipe import (
    create_recipe, 
    get_recipe_by_id, 
    update_recipe, 
    favorite_recipe, 
    search_recipes
)
from app.services.comment import create_comment, get_recipe_comments

router = APIRouter()


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_new_recipe(
    recipe: RecipeCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    创建新菜谱
    
    - 需要授权: Bearer Token
    - 返回创建的菜谱信息
    """
    try:
        created_recipe = await create_recipe(recipe, current_user)
        return created_recipe
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建菜谱失败: {str(e)}"
        )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe_detail(
    recipe_id: str = Path(..., description="菜谱ID"),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取菜谱详细信息
    
    - **recipe_id**: 菜谱ID
    - 返回菜谱详细信息
    """
    try:
        recipe = await get_recipe_by_id(recipe_id, current_user)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜谱不存在"
            )
        return recipe
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取菜谱失败: {str(e)}"
        )


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe_detail(
    recipe: RecipeUpdate,
    recipe_id: str = Path(..., description="菜谱ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    更新菜谱信息
    
    - 需要授权: Bearer Token
    - **recipe_id**: 菜谱ID
    - 返回更新后的菜谱信息
    """
    try:
        updated_recipe = await update_recipe(recipe_id, recipe, current_user)
        if not updated_recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜谱不存在或无权更新"
            )
        return updated_recipe
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新菜谱失败: {str(e)}"
        )


@router.post("/{recipe_id}/favorite", status_code=status.HTTP_200_OK)
async def favorite_recipe_toggle(
    recipe_id: str = Path(..., description="菜谱ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    收藏/取消收藏菜谱
    
    - 需要授权: Bearer Token
    - **recipe_id**: 菜谱ID
    - 返回操作结果
    """
    try:
        result = await favorite_recipe(recipe_id, current_user)
        return {"success": True, "is_favorite": result["is_favorite"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"收藏操作失败: {str(e)}"
        )


@router.get("/", response_model=List[RecipeResponse])
async def search_community_recipes(
    params: RecipeSearchParams = Depends(),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    搜索社区菜谱
    
    - 支持多种筛选条件和排序方式
    - 返回菜谱列表及分页信息
    """
    try:
        recipes, total = await search_recipes(params, current_user)
        # 添加分页信息到响应头
        return recipes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索菜谱失败: {str(e)}"
        )


@router.post("/{recipe_id}/reviews", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_recipe_review(
    comment: CommentCreate,
    recipe_id: str = Path(..., description="菜谱ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    为菜谱添加评论
    
    - 需要授权: Bearer Token
    - **recipe_id**: 菜谱ID
    - **rating**: 评分(1-5)
    - **content**: 评论内容
    - **images**: 可选的评论图片
    - 返回创建的评论信息
    """
    try:
        new_comment = await create_comment(recipe_id, comment, current_user)
        return new_comment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加评论失败: {str(e)}"
        )


@router.get("/{recipe_id}/reviews", response_model=CommentListResponse)
async def get_recipe_reviews(
    recipe_id: str = Path(..., description="菜谱ID"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=50, description="每页数量"),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取菜谱评论列表
    
    - **recipe_id**: 菜谱ID
    - **page**: 页码
    - **limit**: 每页数量
    - 返回评论列表及分页信息
    """
    try:
        comments, total = await get_recipe_comments(recipe_id, page, limit, current_user)
        return CommentListResponse(
            comments=comments,
            total=total,
            page=page,
            limit=limit,
            pages=(total + limit - 1) // limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评论失败: {str(e)}"
        )

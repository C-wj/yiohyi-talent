from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional
import logging
from pydantic import ValidationError

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
from app.services.comment import create_comment, get_recipe_comments, delete_comment, like_comment, unlike_comment, reply_comment, get_comment_by_id

router = APIRouter()

# 配置日志
logger = logging.getLogger(__name__)


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


@router.get("/{recipe_id}", response_model=None)
async def get_recipe_detail(
    recipe_id: str = Path(..., description="菜谱ID")
):
    """
    获取菜谱详细信息
    
    - **recipe_id**: 菜谱ID
    - 返回菜谱详细信息
    """
    logger.info(f"尝试获取菜谱 {recipe_id}")
    try:
        recipe = await get_recipe_by_id(recipe_id)
        if not recipe:
            logger.warning(f"未找到菜谱 {recipe_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜谱不存在"
            )
        logger.info(f"成功获取菜谱 {recipe_id}: {recipe.get('title', 'unknown')}")
        # 直接返回字典，不使用Pydantic模型转换
        return recipe
    except HTTPException as he:
        logger.error(f"请求处理失败 - HTTP异常: {str(he)}")
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"请求处理失败 - 获取菜谱失败: {str(e)}")
        logger.error(f"错误详情: {error_trace}")
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
    params: RecipeSearchParams = Depends()
):
    """
    搜索社区菜谱
    
    - 支持多种筛选条件和排序方式
    - 返回菜谱列表及分页信息
    """
    try:
        recipes, total = await search_recipes(params)
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
    limit: int = Query(10, ge=1, le=50, description="每页数量")
):
    """
    获取菜谱评论列表
    
    - **recipe_id**: 菜谱ID
    - **page**: 页码
    - **limit**: 每页数量
    - 返回评论列表及分页信息
    """
    try:
        comments, total = await get_recipe_comments(recipe_id, page, limit)
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


@router.delete("/{recipe_id}/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe_review(
    recipe_id: str = Path(..., description="菜谱ID"),
    review_id: str = Path(..., description="评论ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    删除评论（仅作者或管理员可删）
    """
    ok = await delete_comment(recipe_id, review_id, current_user)
    if not ok:
        raise HTTPException(status_code=404, detail="评论不存在或无权删除")
    return {"success": True}


@router.post("/{recipe_id}/reviews/{review_id}/like", status_code=status.HTTP_200_OK)
async def like_recipe_review(
    recipe_id: str = Path(..., description="菜谱ID"),
    review_id: str = Path(..., description="评论ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    点赞评论
    """
    ok = await like_comment(review_id, str(current_user["_id"]))
    return {"success": ok}


@router.delete("/{recipe_id}/reviews/{review_id}/like", status_code=status.HTTP_200_OK)
async def unlike_recipe_review(
    recipe_id: str = Path(..., description="菜谱ID"),
    review_id: str = Path(..., description="评论ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    取消点赞评论
    """
    ok = await unlike_comment(review_id, str(current_user["_id"]))
    return {"success": ok}


@router.post("/{recipe_id}/reviews/{review_id}/reply", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def reply_recipe_review(
    comment: CommentCreate,
    recipe_id: str = Path(..., description="菜谱ID"),
    review_id: str = Path(..., description="父评论ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    回复评论
    """
    return await reply_comment(recipe_id, review_id, comment, current_user)


@router.get("/{recipe_id}/reviews/{review_id}", response_model=CommentResponse)
async def get_recipe_review_detail(
    recipe_id: str = Path(..., description="菜谱ID"),
    review_id: str = Path(..., description="评论ID")
):
    """
    获取单条评论详情
    """
    comment = await get_comment_by_id(recipe_id, review_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return comment

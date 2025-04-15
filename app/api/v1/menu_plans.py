from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional

from app.api.dependencies import get_current_user
from app.models.menu_plan import (
    MenuPlanCreate, 
    MenuPlanUpdate, 
    MenuPlanResponse, 
    MenuPlanListParams,
    DishAdd
)
from app.services.menu_plan import (
    create_menu_plan,
    get_menu_plan_by_id,
    update_menu_plan,
    add_dish_to_menu,
    get_family_menu_plans
)

router = APIRouter()


@router.post("/", response_model=MenuPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_new_menu_plan(
    plan: MenuPlanCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    创建新的菜单计划
    
    - 需要授权: Bearer Token
    - 返回创建的菜单计划信息
    """
    try:
        created_plan = await create_menu_plan(plan, current_user)
        return created_plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建菜单计划失败: {str(e)}"
        )


@router.get("/{plan_id}", response_model=MenuPlanResponse)
async def get_menu_plan_detail(
    plan_id: str = Path(..., description="菜单计划ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取菜单计划详细信息
    
    - 需要授权: Bearer Token
    - **plan_id**: 菜单计划ID
    - 返回菜单计划详细信息
    """
    try:
        plan = await get_menu_plan_by_id(plan_id, current_user)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单计划不存在或无权访问"
            )
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取菜单计划失败: {str(e)}"
        )


@router.put("/{plan_id}", response_model=MenuPlanResponse)
async def update_menu_plan_detail(
    plan_data: MenuPlanUpdate,
    plan_id: str = Path(..., description="菜单计划ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    更新菜单计划信息
    
    - 需要授权: Bearer Token
    - **plan_id**: 菜单计划ID
    - 返回更新后的菜单计划信息
    """
    try:
        updated_plan = await update_menu_plan(plan_id, plan_data, current_user)
        if not updated_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单计划不存在或无权更新"
            )
        return updated_plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新菜单计划失败: {str(e)}"
        )


@router.post("/{plan_id}/dishes", response_model=MenuPlanResponse)
async def add_dish_to_menu_plan(
    dish: DishAdd,
    plan_id: str = Path(..., description="菜单计划ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    向菜单添加菜品
    
    - 需要授权: Bearer Token
    - **plan_id**: 菜单计划ID
    - 返回更新后的菜单计划信息
    """
    try:
        updated_plan = await add_dish_to_menu(plan_id, dish, current_user)
        if not updated_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单计划不存在或无权更新"
            )
        return updated_plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加菜品失败: {str(e)}"
        )


@router.get("/by-family/{family_id}", response_model=List[MenuPlanResponse])
async def get_family_menu_plan_list(
    family_id: str = Path(..., description="家庭ID"),
    params: MenuPlanListParams = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    获取指定家庭的菜单计划
    
    - 需要授权: Bearer Token
    - **family_id**: 家庭ID
    - 支持过滤和分页
    - 返回菜单计划列表
    """
    try:
        # 确保使用family_id参数
        params.familyId = family_id
        
        plans, total = await get_family_menu_plans(params, current_user)
        
        # 可以在这里处理分页信息，如添加到响应头
        
        return plans
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取菜单计划列表失败: {str(e)}"
        )


@router.get("/", response_model=List[MenuPlanResponse])
async def get_user_menu_plans(
    params: MenuPlanListParams = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前用户的菜单计划
    
    - 需要授权: Bearer Token
    - 获取用户所有家庭的菜单计划
    - 支持过滤和分页
    - 返回菜单计划列表
    """
    try:
        # 确保familyId为None，这将查询用户所有家庭的菜单计划
        params.familyId = None
        
        plans, total = await get_family_menu_plans(params, current_user)
        
        # 可以在这里处理分页信息，如添加到响应头
        
        return plans
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取菜单计划列表失败: {str(e)}"
        )

from datetime import timedelta
from typing import Any, Dict

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import (ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user,
                          create_access_token, get_current_active_user,
                          get_current_user, get_password_hash,
                          update_last_login)
from app.core.config import settings
from app.db.mongodb import get_collection, db
from app.models.user import Token, UserCreate, UserModel, UserResponse, BaseResponse, PhoneNumberRequest, VerifySMSRequest

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录获取访问令牌"""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """注册新用户"""
    # 检查用户名是否已存在
    if await get_user(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if await get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建用户数据
    user_dict = user_data.dict()
    password = user_dict.pop("password")
    user_dict["passwordHash"] = get_password_hash(password)
    user_dict["isActive"] = True
    user_dict["isVerified"] = False
    user_dict["favorites"] = []
    user_dict["following"] = []
    user_dict["followers"] = []
    
    # 插入数据库
    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    
    # 返回用户信息
    return UserResponse(
        status="success",
        data=user_dict,
        message="用户注册成功"
    )


@router.get("/me", response_model=UserResponse)
async def get_user_me(current_user: Dict[str, Any] = Depends(get_active_user)):
    """获取当前用户信息"""
    return UserResponse(
        status="success",
        data=current_user,
        message="获取用户信息成功"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: UserModel = Depends(get_current_user)) -> Any:
    """
    刷新访问令牌
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/send-sms", response_model=BaseResponse)
async def send_sms_code(phone_data: PhoneNumberRequest):
    """发送短信验证码"""
    phone_number = phone_data.phone_number
    
    # 检查手机号格式
    if not is_valid_phone_number(phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的手机号码"
        )
    
    # 生成验证码
    code = generate_sms_code()
    
    # 存储验证码(使用缓存系统，如Redis)
    await store_sms_code(phone_number, code)
    
    # 发送短信
    success = await send_sms(phone_number, code)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="短信发送失败，请稍后重试"
        )
    
    return BaseResponse(
        status="success",
        message="验证码已发送",
        data={"expires_in": SMS_CODE_EXPIRE_MINUTES}
    )


@router.post("/verify-sms", response_model=Token)
async def verify_sms_code(verify_data: VerifySMSRequest):
    """验证短信验证码并登录"""
    phone_number = verify_data.phone_number
    code = verify_data.code
    
    # 验证码校验
    is_valid = await verify_sms_code(phone_number, code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )
    
    # 查找或创建用户
    user = await get_or_create_user_by_phone(phone_number)
    
    # 生成token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"} 
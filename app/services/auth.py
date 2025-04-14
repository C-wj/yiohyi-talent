from datetime import datetime
from typing import Dict, Any, Tuple

from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, create_refresh_token
from app.models.user import UserProfile, UserStats, Gender
from app.schemas.user import Token
from app.services.user import get_user_by_openid, create_user, update_user_last_login
from app.utils.wechat import code2session


async def wechat_login(code: str, user_info: Dict[str, Any] = None) -> Tuple[Dict[str, Any], Token, str]:
    """
    微信小程序登录
    
    参数:
        code: 小程序登录时获取的临时登录凭证code
        user_info: 可选的用户信息（包含昵称、头像等）
    
    返回:
        Tuple[用户信息, 认证令牌, session_key]
    """
    # 使用code获取微信openid和session_key
    wx_session = code2session(code)
    
    if "openid" not in wx_session:
        raise AuthenticationError(detail="微信登录失败: 无法获取openid")
    
    openid = wx_session["openid"]
    session_key = wx_session.get("session_key", "")
    unionid = wx_session.get("unionid")
    
    # 检查用户是否已存在
    user = await get_user_by_openid(openid)
    
    if not user:
        # 创建新用户
        user_data = {
            "openid": openid,
            "unionid": unionid,
            "profile": {
                "nickname": f"用户{openid[-6:]}",  # 默认昵称
                "gender": Gender.UNKNOWN.value,
            },
            "stats": {
                "recipe_count": 0,
                "favorite_count": 0,
                "order_count": 0,
                "followers_count": 0,
                "following_count": 0,
            },
            "is_active": True,
            "is_verified": False,
            "last_login": datetime.utcnow(),
        }
        
        # 如果提供了用户信息，更新资料
        if user_info and isinstance(user_info, dict):
            nickname = user_info.get("nickName", user_data["profile"]["nickname"])
            avatar = user_info.get("avatarUrl")
            gender_map = {0: Gender.UNKNOWN.value, 1: Gender.MALE.value, 2: Gender.FEMALE.value}
            gender = gender_map.get(user_info.get("gender", 0), Gender.UNKNOWN.value)
            
            user_data["profile"] = {
                "nickname": nickname,
                "avatar": avatar,
                "gender": gender,
            }
        
        user = await create_user(user_data)
    else:
        # 更新登录时间
        await update_user_last_login(user["_id"])
    
    # 生成认证令牌
    access_token = create_access_token(subject=user["_id"])
    refresh_token = create_refresh_token(subject=user["_id"])
    
    token = Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
    
    return user, token, session_key


async def refresh_token(refresh_token: str) -> Token:
    """
    刷新访问令牌
    
    参数:
        refresh_token: 刷新令牌
    
    返回:
        新的认证令牌
    """
    from app.core.security import decode_token
    
    try:
        # 验证刷新令牌
        payload = decode_token(refresh_token)
        
        # 确认是刷新令牌
        if payload.get("type") != "refresh":
            raise AuthenticationError(detail="无效的刷新令牌")
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError(detail="无效的用户ID")
        
        # 生成新的令牌
        new_access_token = create_access_token(subject=user_id)
        new_refresh_token = create_refresh_token(subject=user_id)
        
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    except Exception as e:
        raise AuthenticationError(detail=f"刷新令牌失败: {str(e)}") 
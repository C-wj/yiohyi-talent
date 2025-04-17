from datetime import datetime
from typing import Dict, Any, Tuple

from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, create_refresh_token
from app.models.user import UserProfile, UserStats, Gender
from app.schemas.user import Token
from app.services.user import get_user_by_openid, create_user, update_user_last_login, get_user_by_phone, get_user_by_account
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


async def password_login(account: str, password: str) -> Token:
    """
    使用账号密码登录
    
    参数:
        account: 用户账号(手机号或者用户名)
        password: 用户密码
    
    返回:
        认证令牌
    """
    from app.core.security import verify_password
    
    try:
        # 查询用户
        user = await get_user_by_account(account)
        
        if not user:
            raise AuthenticationError(detail="用户不存在")
        
        # 验证密码
        if not user.get("password_hash") or not verify_password(password, user["password_hash"]):
            raise AuthenticationError(detail="密码错误")
        
        # 检查用户状态
        if not user.get("is_active", False):
            raise AuthenticationError(detail="用户已被禁用")
        
        # 更新登录时间
        await update_user_last_login(user["_id"])
        
        # 生成认证令牌
        access_token = create_access_token(subject=user["_id"])
        refresh_token = create_refresh_token(subject=user["_id"])
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    except AuthenticationError:
        raise
    except Exception as e:
        raise AuthenticationError(detail=f"账号密码登录失败: {str(e)}")


async def send_sms_code(phone_number: str) -> Dict[str, Any]:
    """
    发送短信验证码
    
    参数:
        phone_number: 手机号码
    
    返回:
        发送结果
    """
    # 短信验证码模拟实现
    # 在实际生产环境中，需要对接SMS服务提供商API
    try:
        from app.db.redis import get_redis
        import random
        
        # 生成6位随机验证码
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # 存储验证码到Redis，过期时间5分钟
        redis = await get_redis()
        await redis.set(f"sms:code:{phone_number}", code, ex=300)
        
        # 模拟发送短信
        # 在实际生产环境中，这里应调用短信服务API
        print(f"【家宴菜谱】验证码: {code}, 有效期5分钟。")
        
        return {"success": True, "message": "验证码已发送"}
    except Exception as e:
        raise Exception(f"发送验证码失败: {str(e)}")


async def verify_sms_code(phone_number: str, code: str) -> Token:
    """
    验证短信验证码并登录
    
    参数:
        phone_number: 手机号码
        code: 验证码
    
    返回:
        认证令牌
    """
    try:
        from app.db.redis import get_redis
        
        # 从Redis获取验证码
        redis = await get_redis()
        stored_code = await redis.get(f"sms:code:{phone_number}")
        
        if not stored_code:
            raise AuthenticationError(detail="验证码已过期")
        
        # 验证码比对
        if code != stored_code.decode():
            raise AuthenticationError(detail="验证码错误")
        
        # 验证通过后删除验证码
        await redis.delete(f"sms:code:{phone_number}")
        
        # 查询用户是否存在
        user = await get_user_by_phone(phone_number)
        
        if not user:
            # 创建新用户
            user_data = {
                "phone": phone_number,
                "profile": {
                    "nickname": f"用户{phone_number[-4:]}",  # 默认昵称
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
                "is_verified": True,  # 手机验证通过
                "last_login": datetime.utcnow(),
            }
            user = await create_user(user_data)
        else:
            # 更新登录时间
            await update_user_last_login(user["_id"])
        
        # 生成认证令牌
        access_token = create_access_token(subject=user["_id"])
        refresh_token = create_refresh_token(subject=user["_id"])
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    except AuthenticationError:
        raise
    except Exception as e:
        raise AuthenticationError(detail=f"验证码登录失败: {str(e)}") 
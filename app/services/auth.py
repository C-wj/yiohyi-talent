from datetime import datetime
from typing import Dict, Any, Tuple

from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, create_refresh_token
from app.models.user import UserProfile, UserStats, Gender,Token
from app.services.user import get_user_by_openid, create_user, update_user_last_login, get_user_by_phone, get_user_by_account, get_user_by_email, get_user_by_username
from app.utils.wechat import code2session
from app.utils.email import send_email


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
        account: 用户账号(手机号或者用户名或邮箱)
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


async def logout(token: str) -> Dict[str, Any]:
    """
    用户登出，将令牌加入黑名单
    
    参数:
        token: 访问令牌
    
    返回:
        登出结果
    """
    try:
        from app.db.redis import get_redis
        from app.core.security import decode_token
        
        # 解码令牌以获取过期时间
        payload = decode_token(token)
        exp = payload.get("exp", 0)
        jti = payload.get("jti", "")  # 如果令牌中有唯一标识符
        
        # 计算剩余有效时间（秒）
        now = datetime.utcnow().timestamp()
        ttl = max(int(exp - now), 0)
        
        # 获取Redis连接
        redis = await get_redis()
        
        # 将令牌加入黑名单，保存到令牌过期时间
        blacklist_key = f"token:blacklist:{token}" if not jti else f"token:blacklist:{jti}"
        await redis.set(blacklist_key, "1", ex=ttl)
        
        return {"success": True, "message": "登出成功"}
    except Exception as e:
        raise Exception(f"登出失败: {str(e)}")


async def is_token_blacklisted(token: str) -> bool:
    """
    检查令牌是否已被加入黑名单
    
    参数:
        token: 访问令牌
    
    返回:
        如果令牌在黑名单中返回True，否则返回False
    """
    try:
        from app.db.redis import get_redis
        from app.core.security import decode_token
        
        # 获取令牌唯一标识符（如果有）
        try:
            payload = decode_token(token)
            jti = payload.get("jti", "")
        except:
            # 如果令牌解码失败，认为令牌无效
            return True
        
        # 获取Redis连接
        redis = await get_redis()
        
        # 检查完整令牌或JTI是否在黑名单中
        blacklist_key = f"token:blacklist:{token}" if not jti else f"token:blacklist:{jti}"
        result = await redis.get(blacklist_key)
        
        return result is not None
    except Exception as e:
        # 如果发生错误，为安全起见，返回True
        print(f"检查令牌黑名单失败: {str(e)}")
        return False


async def send_password_reset_email(email: str) -> Dict[str, Any]:
    """
    发送密码重置邮件
    
    参数:
        email: 用户邮箱
    
    返回:
        发送结果
    """
    try:
        from app.core.security import generate_password_reset_token
        from app.utils.email import send_email
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"正在处理密码重置请求: {email}")
        
        # 查询用户是否存在
        user = await get_user_by_email(email)
        if not user:
            logger.warning(f"密码重置请求失败: 邮箱不存在 {email}")
            return {"success": False, "message": "用户不存在"}
        
        # 生成密码重置令牌
        reset_token = generate_password_reset_token(email)
        
        # 构建重置链接
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        # 构建邮件内容
        subject = "【家宴菜谱】密码重置请求"
        
        # 使用HTML格式的邮件内容，提供更好的用户体验
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 10px; text-align: center; }}
                .content {{ padding: 20px 0; }}
                .button {{ display: inline-block; background-color: #4CAF50; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 4px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #777; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>密码重置请求</h2>
                </div>
                <div class="content">
                    <p>您好，</p>
                    <p>我们收到了您的密码重置请求。请点击下面的按钮重置您的密码：</p>
                    <p style="text-align: center;">
                        <a href="{reset_link}" class="button">重置密码</a>
                    </p>
                    <p>或者，您可以复制以下链接到浏览器地址栏：</p>
                    <p>{reset_link}</p>
                    <p>此链接将在24小时后失效。如果您没有请求重置密码，请忽略此邮件。</p>
                </div>
                <div class="footer">
                    <p>此致，</p>
                    <p>家宴菜谱团队</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 发送邮件
        send_result = await send_email(to_email=email, subject=subject, body=body, is_html=True)
        
        if send_result:
            logger.info(f"密码重置邮件发送成功: {email}")
        else:
            logger.error(f"密码重置邮件发送失败: {email}")
        
        return {"success": send_result, "message": "密码重置邮件已发送" if send_result else "邮件发送失败"}
    except Exception as e:
        logger.error(f"发送密码重置邮件失败: {str(e)}")
        raise Exception(f"发送密码重置邮件失败: {str(e)}")


async def reset_password(token: str, new_password: str) -> Dict[str, Any]:
    """
    重置密码
    
    参数:
        token: 密码重置令牌
        new_password: 新密码
    
    返回:
        重置结果
    """
    try:
        from app.core.security import verify_password_reset_token, get_password_hash
        from app.services.user import get_user_by_email, update_user
        import logging
        import re
        
        logger = logging.getLogger(__name__)
        logger.info("开始处理密码重置")
        
        # 验证密码强度
        if len(new_password) < 8:
            logger.warning("密码重置失败：密码太短")
            raise ValueError("密码长度不能少于8个字符")
        
        # 检查密码复杂度：至少包含一个数字和一个字母
        if not re.search(r'\d', new_password) or not re.search(r'[a-zA-Z]', new_password):
            logger.warning("密码重置失败：密码复杂度不足")
            raise ValueError("密码必须包含至少一个数字和一个字母")
        
        # 验证重置令牌
        try:
            email = verify_password_reset_token(token)
            logger.info(f"密码重置令牌验证成功，用户邮箱: {email}")
        except Exception as e:
            logger.error(f"密码重置令牌验证失败: {str(e)}")
            raise ValueError(f"无效的密码重置令牌: {str(e)}")
        
        # 获取用户
        user = await get_user_by_email(email)
        if not user:
            logger.error(f"密码重置失败：用户不存在，邮箱: {email}")
            raise ValueError("用户不存在")
        
        # 哈希新密码
        password_hash = get_password_hash(new_password)
        
        # 更新用户密码
        update_data = {
            "password_hash": password_hash,
            "updated_at": datetime.utcnow()
        }
        
        try:
            # update_user 会返回更新后的用户文档，如果执行成功
            updated_user = await update_user(user["_id"], update_data)
            logger.info(f"密码重置成功，用户邮箱: {email}")
            
            # 发送密码更改通知邮件
            try:
                from app.utils.email import send_email
                
                subject = "【家宴菜谱】密码已更改"
                body = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #f8f9fa; padding: 10px; text-align: center; }}
                        .content {{ padding: 20px 0; }}
                        .footer {{ margin-top: 20px; font-size: 12px; color: #777; text-align: center; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>密码已更改</h2>
                        </div>
                        <div class="content">
                            <p>您好，</p>
                            <p>您的家宴菜谱账号密码已成功重置。</p>
                            <p>此操作是在 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} (UTC) 完成的。</p>
                            <p>如果这不是您本人操作，请立即联系我们的客服团队。</p>
                        </div>
                        <div class="footer">
                            <p>此致，</p>
                            <p>家宴菜谱团队</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                # 异步发送通知邮件，不影响密码重置流程
                await send_email(to_email=email, subject=subject, body=body, is_html=True)
                logger.info(f"已发送密码更改通知邮件到: {email}")
            except Exception as email_error:
                # 只记录日志，不影响密码重置流程
                logger.warning(f"发送密码更改通知邮件失败: {str(email_error)}")
            
            return {"success": True, "message": "密码重置成功"}
        except Exception as db_error:
            logger.error(f"密码重置失败：数据库更新失败，用户邮箱: {email}, 错误: {str(db_error)}")
            raise ValueError(f"密码更新失败: {str(db_error)}")
    except ValueError as e:
        logger.error(f"密码重置失败(验证错误): {str(e)}")
        raise ValueError(f"密码重置失败: {str(e)}")
    except Exception as e:
        logger.error(f"密码重置失败(系统错误): {str(e)}")
        raise Exception(f"密码重置失败: {str(e)}")


async def register_user(register_data) -> Token:
    """
    用户注册
    
    参数:
        register_data: 注册数据，包含username、password、nickname等
    
    返回:
        认证令牌
    """
    try:
        from app.core.security import get_password_hash
        from app.services.user import get_user_by_username, get_user_by_email, get_user_by_phone, create_user
        import re
        
        # 验证用户名格式
        if not register_data.username:
            raise AuthenticationError(detail="缺少必要的用户名")
            
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', register_data.username):
            raise AuthenticationError(detail="用户名格式错误，只能包含字母、数字和下划线，长度3-20位")
        
        # 验证密码强度
        if not register_data.password:
            raise AuthenticationError(detail="缺少必要的密码")
            
        if len(register_data.password) < 8:
            raise AuthenticationError(detail="密码长度不能少于8个字符")
        
        # 检查密码复杂度：至少包含一个数字和一个字母
        if not re.search(r'\d', register_data.password) or not re.search(r'[a-zA-Z]', register_data.password):
            raise AuthenticationError(detail="密码必须包含至少一个数字和一个字母")
        
        # 检查用户名是否已存在
        existing_user = await get_user_by_username(register_data.username)
        if existing_user:
            raise AuthenticationError(detail="用户名已存在")
        
        # 如果提供了邮箱，检查邮箱是否已存在
        if register_data.email:
            existing_user = await get_user_by_email(register_data.email)
            if existing_user:
                raise AuthenticationError(detail="邮箱已注册")
        
        # 如果提供了手机号，检查手机号是否已存在
        if register_data.phone:
            if not re.match(r'^1[3-9]\d{9}$', register_data.phone):
                raise AuthenticationError(detail="手机号格式错误")
                
            existing_user = await get_user_by_phone(register_data.phone)
            if existing_user:
                raise AuthenticationError(detail="手机号已注册")
        
        # 设置昵称（如果未提供，使用用户名）
        nickname = register_data.nickname if register_data.nickname else register_data.username
        
        # 创建用户
        now = datetime.utcnow()
        user_data = {
            "username": register_data.username,
            "password_hash": get_password_hash(register_data.password),
            "email": register_data.email,
            "phone": register_data.phone,
            "profile": {
                "nickname": nickname,
                "gender": Gender.UNKNOWN.value
            },
            "stats": {
                "recipe_count": 0,
                "favorite_count": 0,
                "order_count": 0,
                "followers_count": 0,
                "following_count": 0
            },
            "is_active": True,
            "is_verified": False,
            "created_at": now,
            "updated_at": now,
            "last_login": now
        }
        
        user = await create_user(user_data)
        
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
        raise AuthenticationError(detail=f"注册失败: {str(e)}") 
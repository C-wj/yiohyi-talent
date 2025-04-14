import json
import logging
from typing import Dict, Any, Optional, Tuple

import requests
from wechatpy.exceptions import WeChatClientException

from app.core.config import settings
from app.core.exceptions import WechatAPIError

# 微信小程序API基础URL
WECHAT_API_URL = "https://api.weixin.qq.com"


def code2session(code: str) -> Dict[str, Any]:
    """
    使用临时登录凭证获取用户的openid和session_key
    
    微信小程序登录接口: https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html
    """
    try:
        api_url = f"{WECHAT_API_URL}/sns/jscode2session"
        params = {
            "appid": settings.WECHAT_MINI_APP_ID,
            "secret": settings.WECHAT_MINI_APP_SECRET,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        
        response = requests.get(api_url, params=params)
        result = response.json()
        
        if 'errcode' in result and result['errcode'] != 0:
            error_msg = f"微信登录失败: {result.get('errmsg', '未知错误')}"
            logging.error(f"{error_msg}, 错误码: {result.get('errcode')}")
            raise WechatAPIError(detail=error_msg)
        
        # 成功返回包含openid和session_key
        return result
    except (requests.RequestException, WeChatClientException, json.JSONDecodeError) as e:
        error_msg = f"微信API调用异常: {str(e)}"
        logging.error(error_msg)
        raise WechatAPIError(detail=error_msg)


def decrypt_user_info(session_key: str, encrypted_data: str, iv: str) -> Dict[str, Any]:
    """
    解密用户信息
    
    微信小程序解密用户信息: https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/signature.html#解密算法
    """
    try:
        from wechatpy.crypto import WeChatCrypto
        
        # 创建加密对象
        crypto = WeChatCrypto(settings.WECHAT_MINI_APP_ID, session_key, settings.WECHAT_MINI_APP_ID)
        
        # 解密数据
        decrypted_data = crypto.decrypt_message(encrypted_data, iv)
        return json.loads(decrypted_data)
    except (WeChatClientException, json.JSONDecodeError) as e:
        error_msg = f"解密用户信息失败: {str(e)}"
        logging.error(error_msg)
        raise WechatAPIError(detail=error_msg)


def get_access_token() -> str:
    """
    获取微信小程序全局接口调用凭证
    
    微信小程序获取access_token: https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/access-token/auth.getAccessToken.html
    """
    try:
        api_url = f"{WECHAT_API_URL}/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": settings.WECHAT_MINI_APP_ID,
            "secret": settings.WECHAT_MINI_APP_SECRET
        }
        
        response = requests.get(api_url, params=params)
        result = response.json()
        
        if 'errcode' in result and result['errcode'] != 0:
            error_msg = f"获取access_token失败: {result.get('errmsg', '未知错误')}"
            logging.error(f"{error_msg}, 错误码: {result.get('errcode')}")
            raise WechatAPIError(detail=error_msg)
        
        # 成功返回
        return result.get("access_token")
    except (requests.RequestException, WeChatClientException, json.JSONDecodeError) as e:
        error_msg = f"获取access_token异常: {str(e)}"
        logging.error(error_msg)
        raise WechatAPIError(detail=error_msg)


def generate_mini_qrcode(scene: str, path: Optional[str] = None) -> bytes:
    """
    生成小程序码
    
    微信小程序码生成: https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/qr-code/wxacode.getUnlimited.html
    """
    try:
        access_token = get_access_token()
        api_url = f"{WECHAT_API_URL}/wxa/getwxacodeunlimit?access_token={access_token}"
        
        data = {
            "scene": scene,
            "check_path": False,
            "env_version": "release"  # 正式版
        }
        
        if path:
            data["page"] = path
        
        response = requests.post(api_url, json=data)
        
        # 判断返回是否为图片
        if response.headers.get("Content-Type").startswith("image/"):
            return response.content
        
        # 不是图片，可能是错误信息
        result = response.json()
        error_msg = f"生成小程序码失败: {result.get('errmsg', '未知错误')}"
        logging.error(f"{error_msg}, 错误码: {result.get('errcode')}")
        raise WechatAPIError(detail=error_msg)
    except (requests.RequestException, WeChatClientException, json.JSONDecodeError) as e:
        error_msg = f"生成小程序码异常: {str(e)}"
        logging.error(error_msg)
        raise WechatAPIError(detail=error_msg) 
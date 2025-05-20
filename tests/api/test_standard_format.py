"""
测试API标准格式
确保所有API响应都遵循标准格式 {code: 0, data: object, msg: ''}
"""
import json
import pytest
from typing import Dict, Any, List
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# 测试URL列表
TEST_URLS = [
    # 基础URL
    {"url": "/", "method": "get"},
    {"url": "/health", "method": "get"},
    
    # 首页相关API
    {"url": "/api/v1/home/cards", "method": "get"},
    {"url": "/api/v1/home/swipers", "method": "get"},
    {"url": "/api/v1/home/recommended", "method": "get"},
    {"url": "/api/v1/home/seasonal", "method": "get"},
    
    # 需要认证的API，但我们只验证401响应格式是否标准
    {"url": "/api/v1/users/profile", "method": "get", "auth_required": True},
]

def test_response_format():
    """测试API响应格式"""
    for test_case in TEST_URLS:
        url = test_case["url"]
        method = test_case["method"]
        auth_required = test_case.get("auth_required", False)
        
        if method == "get":
            response = client.get(url)
        elif method == "post":
            response = client.post(url, json={})
        else:
            pytest.skip(f"不支持的HTTP方法: {method}")
            continue
        
        print(f"Testing {method.upper()} {url}, Status: {response.status_code}")
        
        assert response.status_code == 200, f"API {url} 状态码不是200: {response.status_code}"
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            pytest.fail(f"API {url} 返回的不是有效的JSON")
        
        # 验证响应格式
        assert "code" in data, f"API {url} 响应中缺少code字段"
        assert "data" in data, f"API {url} 响应中缺少data字段"
        assert "msg" in data, f"API {url} 响应中缺少msg字段"
        
        # 如果需要认证，验证401响应格式
        if auth_required and data["code"] == 401:
            assert data["msg"], "缺少401错误消息"


def test_error_format():
    """测试错误响应格式"""
    # 测试404错误
    response = client.get("/api/v1/not-exist-endpoint")
    assert response.status_code == 200, "错误响应状态码应为200"
    
    data = response.json()
    assert "code" in data, "错误响应中缺少code字段"
    assert data["code"] == 404, "404错误的code应为404"
    assert "msg" in data, "错误响应中缺少msg字段"
    assert "data" in data, "错误响应中缺少data字段"
    
    # 测试校验错误
    response = client.post("/api/v1/auth/register", json={"invalid": "data"})
    assert response.status_code == 200, "验证错误响应状态码应为200"
    
    data = response.json()
    assert "code" in data, "验证错误响应中缺少code字段"
    assert data["code"] == 422, "验证错误的code应为422"
    assert "msg" in data, "验证错误响应中缺少msg字段"
    assert "data" in data, "验证错误响应中缺少data字段"


if __name__ == "__main__":
    # 直接运行测试
    pytest.main(["-xvs", __file__]) 
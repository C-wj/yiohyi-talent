import requests
import sys
import time

def check_service(url="http://localhost:8000", max_retries=5, retry_interval=1):
    """检查服务是否正常运行"""
    print(f"检查服务 {url} 是否正常运行...")
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"服务正常运行! 状态: {data.get('status')}, 版本: {data.get('version')}")
                return True
            else:
                print(f"尝试 {i+1}/{max_retries}: 服务返回状态码 {response.status_code}")
        except requests.RequestException as e:
            print(f"尝试 {i+1}/{max_retries}: 连接失败 - {str(e)}")
        
        if i < max_retries - 1:
            print(f"等待 {retry_interval} 秒后重试...")
            time.sleep(retry_interval)
    
    print("服务检查失败，无法连接到服务。")
    return False

def check_docs(url="http://localhost:8000"):
    """检查API文档是否可用"""
    try:
        response = requests.get(f"{url}/docs")
        if response.status_code == 200:
            print("API文档(Swagger UI)可用!")
            return True
        else:
            print(f"API文档检查失败，状态码: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"API文档检查失败 - {str(e)}")
        return False

if __name__ == "__main__":
    url = "http://localhost:8000"
    
    # 检查服务健康状态
    service_ok = check_service(url)
    
    if service_ok:
        # 检查API文档
        docs_ok = check_docs(url)
        
        # 打印访问信息
        print("\n服务已成功启动，可以通过以下URL访问:")
        print(f"- 主页: {url}/")
        print(f"- API文档: {url}/docs")
        print(f"- 健康检查: {url}/health")
        
        sys.exit(0)
    else:
        print("\n服务启动失败，请检查日志以获取更多信息。")
        sys.exit(1) 
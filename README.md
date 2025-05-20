# 家宴菜谱小程序后台服务

## 项目介绍

"家宴"是一款家庭菜谱管理与分享的微信小程序，本项目是其后台服务部分，使用Python/FastAPI开发。

主要功能包括：
- 用户认证与管理
- 菜谱创建、管理与分享
- 家庭群组创建与管理
- 家庭点菜系统
- 购物清单生成与管理
- 食材智能管理

## 技术栈

- **编程语言**: Python 3.10+
- **Web框架**: FastAPI
- **数据库**: MongoDB
- **缓存**: Redis (可选)
- **任务队列**: Celery
- **容器化**: Docker & Docker Compose
- **文档**: Swagger/ReDoc (自动生成)

## 本地开发环境设置

### 前置要求

- Python 3.10+
- MongoDB
- Redis (可选)
- Docker & Docker Compose (可选，用于容器化部署)

### 安装步骤

1. 克隆代码库
   ```bash
   git clone https://github.com/yourusername/yiohyi-talent.git
   cd yiohyi-talent
   ```

2. 创建并激活虚拟环境
   ```bash
   python -m venv venv
   # Linux/MacOS
   source venv/bin/activate
   # Windows
   venv\Scripts\activate
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 环境配置
   ```bash
   cp .env.example .env
   # 编辑.env文件，填入必要的配置信息
   ```

5. 启动开发服务器
   ```bash
   python -m app.main
   ```

### 使用Docker启动

```bash
docker-compose up -d
```

## API文档

启动服务器后，可通过以下URL访问API文档：
- Swagger UI: http://localhost:9091/docs
- ReDoc: http://localhost:9091/redoc

## 开发规范

- 代码风格遵循PEP 8
- 使用类型提示
- 编写单元测试
- 使用Git Flow工作流
- 提交前运行代码格式化工具(black, isort)

## 项目结构

参见 [project_structure.md](project_structure.md) 文件，其中详细描述了项目的目录结构和各模块职责。

## 部署

### 部署到生产环境

1. 确保生产环境配置文件正确
   ```bash
   cp .env.example .env.prod
   # 编辑.env.prod文件，配置生产环境参数
   ```

2. 使用Docker Compose部署
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### 手动部署

参见 [deployment.md](docs/deployment.md) 文件，其中包含详细的部署指南。

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

[MIT](LICENSE)

## 联系方式

有任何问题或建议，请通过以下方式联系我们：
- 电子邮件: your-email@example.com
- GitHub Issues: https://github.com/yourusername/yiohyi-talent/issues

## API标准格式

为确保前后端交互的一致性，所有API响应都遵循以下标准格式：

```json
{
  "code": 0,       // 状态码，0表示成功
  "data": {},      // 业务数据，可以是任意JSON支持的数据类型
  "msg": "success" // 消息说明
}
```

### 状态码说明

- `code = 0`: 成功，前端可以正常处理返回的数据
- `code = 401`: 需要登录，前端需要清除登录状态并引导用户去登录页
- `code = 500`: 系统异常，前端需要提示用户系统异常
- 其他非零值: 业务异常，前端需要显示`msg`字段内容

### 更新API格式

我们提供了一个脚本，可以自动更新所有API路由函数，使用装饰器确保统一的返回格式：

```bash
# 添加执行权限
chmod +x scripts/update_api_format.sh

# 运行脚本
./scripts/update_api_format.sh
```

### 测试API格式

运行以下命令测试API响应格式是否符合标准：

```bash
pytest tests/api/test_standard_format.py -v
```

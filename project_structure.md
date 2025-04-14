# 家宴菜谱微信小程序后台服务 - Python项目结构

## 项目概述

本项目是为"家宴"微信小程序提供的后台服务，使用Python语言开发。主要功能包括用户管理、菜谱管理、家庭管理、点菜系统和购物清单等。

## 技术选型

- **编程语言**: Python 3.10+
- **Web框架**: FastAPI (高性能异步API框架)
- **数据库**: MongoDB (适合存储复杂的菜谱数据结构)
- **身份认证**: JWT (JSON Web Token)
- **云服务**: 微信云开发 / 阿里云 / 腾讯云
- **文件存储**: 云存储 (用于存储菜谱图片等)
- **API文档**: Swagger UI & ReDoc (FastAPI内置)
- **异步任务队列**: Celery (用于处理图像处理、数据分析等耗时任务)
- **容器化**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## 目录结构

```
yiohyi-talent/                    # 项目根目录
├── app/                          # 应用主目录
│   ├── api/                      # API接口模块
│   │   ├── v1/                   # API v1版本
│   │   │   ├── auth.py           # 认证相关API
│   │   │   ├── users.py          # 用户管理API
│   │   │   ├── families.py       # 家庭管理API
│   │   │   ├── recipes.py        # 菜谱管理API
│   │   │   ├── menu_plans.py     # 点菜系统API
│   │   │   ├── shopping_lists.py # 购物清单API
│   │   │   ├── ingredients.py    # 食材管理API
│   │   │   └── uploads.py        # 文件上传API
│   │   ├── dependencies.py       # API依赖项
│   │   └── __init__.py
│   ├── core/                     # 核心模块
│   │   ├── config.py             # 配置管理
│   │   ├── security.py           # 安全相关
│   │   ├── exceptions.py         # 自定义异常
│   │   └── __init__.py
│   ├── db/                       # 数据库模块
│   │   ├── mongodb.py            # MongoDB连接和操作
│   │   ├── redis.py              # Redis连接和操作(可选)
│   │   └── __init__.py
│   ├── models/                   # 数据模型
│   │   ├── user.py               # 用户模型
│   │   ├── family.py             # 家庭模型
│   │   ├── recipe.py             # 菜谱模型
│   │   ├── menu_plan.py          # 点菜菜单模型
│   │   ├── shopping_list.py      # 购物清单模型
│   │   ├── ingredient.py         # 食材模型
│   │   └── __init__.py
│   ├── schemas/                  # Pydantic模型(用于请求/响应验证)
│   │   ├── user.py               # 用户相关模式
│   │   ├── family.py             # 家庭相关模式
│   │   ├── recipe.py             # 菜谱相关模式
│   │   ├── menu_plan.py          # 点菜相关模式
│   │   ├── shopping_list.py      # 购物清单相关模式
│   │   └── __init__.py
│   ├── services/                 # 业务逻辑服务
│   │   ├── auth.py               # 认证服务
│   │   ├── user.py               # 用户服务
│   │   ├── family.py             # 家庭服务
│   │   ├── recipe.py             # 菜谱服务
│   │   ├── menu_plan.py          # 点菜服务
│   │   ├── shopping_list.py      # 购物清单服务
│   │   ├── ingredient.py         # 食材服务
│   │   ├── wechat.py             # 微信相关服务
│   │   └── __init__.py
│   ├── utils/                    # 工具函数
│   │   ├── wechat.py             # 微信API工具
│   │   ├── image.py              # 图像处理工具
│   │   ├── text.py               # 文本处理工具
│   │   ├── validators.py         # 自定义验证器
│   │   └── __init__.py
│   ├── tasks/                    # 异步任务
│   │   ├── task_queue.py         # 任务队列配置
│   │   ├── recipe_tasks.py       # 菜谱相关任务
│   │   ├── notification_tasks.py # 通知相关任务
│   │   └── __init__.py
│   ├── middleware/               # 中间件
│   │   ├── auth_middleware.py    # 认证中间件
│   │   ├── error_handler.py      # 错误处理
│   │   ├── logging_middleware.py # 日志中间件
│   │   └── __init__.py
│   ├── main.py                   # 应用入口点
│   └── __init__.py
├── tests/                        # 测试目录
│   ├── conftest.py               # 测试配置
│   ├── test_api/                 # API测试
│   │   ├── test_auth.py
│   │   ├── test_users.py
│   │   ├── test_recipes.py
│   │   └── ...
│   ├── test_services/            # 服务测试
│   │   ├── test_auth_service.py
│   │   ├── test_recipe_service.py
│   │   └── ...
│   └── __init__.py
├── alembic/                      # 数据库迁移(如使用关系型数据库)
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── static/                       # 静态文件(如有需要)
├── logs/                         # 日志目录
├── docker/                       # Docker相关文件
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
├── scripts/                      # 辅助脚本
│   ├── start.sh
│   ├── deploy.sh
│   └── backup.sh
├── .github/                      # GitHub Actions配置
│   └── workflows/
│       ├── test.yml
│       └── deploy.yml
├── .gitignore                    # Git忽略文件
├── requirements.txt              # 依赖管理
├── .env.example                  # 环境变量示例
├── README.md                     # 项目说明
├── LICENSE                       # 许可证
└── pyproject.toml                # Python项目配置(可选)
```

## 核心模块职责

### 1. API模块 (`app/api/`)

负责接收和处理HTTP请求，将请求传递给服务层，并返回适当的响应。
- **auth.py**: 处理用户登录、注册、Token刷新等
- **users.py**: 用户信息管理
- **families.py**: 家庭创建、成员管理
- **recipes.py**: 菜谱CRUD、收藏、评价
- **menu_plans.py**: 点菜菜单管理
- **shopping_lists.py**: 购物清单管理
- **ingredients.py**: 食材管理API

### 2. 核心模块 (`app/core/`)

处理应用程序配置、安全设置等核心功能。
- **config.py**: 加载和管理配置
- **security.py**: 安全相关功能，如密码哈希、JWT生成
- **exceptions.py**: 自定义异常类

### 3. 数据库模块 (`app/db/`)

封装数据库操作，提供数据访问接口。
- **mongodb.py**: MongoDB连接和CRUD操作
- **redis.py**: 缓存和会话存储(可选)

### 4. 数据模型 (`app/models/`)

定义数据库模型，表示应用程序的主要数据结构。
- **user.py**: 用户模型
- **family.py**: 家庭模型
- **recipe.py**: 菜谱模型
- **menu_plan.py**: 点菜菜单模型
- **shopping_list.py**: 购物清单模型

### 5. Pydantic模式 (`app/schemas/`)

使用Pydantic定义请求和响应的数据格式，进行数据验证。
- **user.py**: 用户相关请求/响应模式
- **recipe.py**: 菜谱相关请求/响应模式
- ...

### 6. 服务层 (`app/services/`)

实现业务逻辑，位于API和数据库之间的中间层。
- **auth.py**: 用户认证
- **recipe.py**: 菜谱相关业务逻辑
- **wechat.py**: 微信相关服务
- ...

### 7. 工具函数 (`app/utils/`)

提供可重用的辅助函数。
- **wechat.py**: 微信API交互
- **image.py**: 图像处理
- **text.py**: 文本处理
- ...

### 8. 异步任务 (`app/tasks/`)

管理耗时操作和后台任务。
- **task_queue.py**: Celery配置
- **recipe_tasks.py**: 菜谱相关任务
- **notification_tasks.py**: 推送通知任务

### 9. 中间件 (`app/middleware/`)

处理请求和响应的拦截器。
- **auth_middleware.py**: 认证中间件
- **error_handler.py**: 错误处理中间件
- **logging_middleware.py**: 日志中间件

## 数据流程

1. 客户端(微信小程序)发送请求到API端点
2. 中间件处理请求(日志、认证等)
3. API路由处理器接收请求并验证输入数据
4. 调用相应的服务执行业务逻辑
5. 服务层与数据库交互，获取或修改数据
6. 服务返回结果给API处理器
7. API处理器将结果格式化并返回给客户端

## 开发流程

1. 设置项目基础框架和依赖
2. 实现核心功能模块(配置、数据库连接)
3. 按优先级实现各API端点:
   - 用户认证API
   - 菜谱管理API
   - 家庭管理API
   - 点菜系统API
   - 购物清单API
4. 添加单元测试和集成测试
5. 设置CI/CD流程
6. 准备部署文档

## 部署架构

```
[微信小程序] <---> [Nginx] <---> [FastAPI服务] <---> [MongoDB]
                      |               |
                      v               v
                  [静态文件]     [Redis缓存]
                                     |
                                     v
                               [Celery Worker]
```

## 安全考虑

- 使用HTTPS确保传输安全
- 实现JWT令牌的有效期和刷新机制
- 对敏感数据进行加密存储
- 实现请求限流防止DoS攻击
- 定期审计和记录关键操作
- 微信登录与服务器认证的安全对接

## 可扩展性设计

1. **模块化结构**: 每个主要功能都被封装在独立的模块中
2. **版本控制的API**: 使用/v1/路径前缀，便于将来API升级
3. **抽象的数据访问层**: 便于将来更换存储方案
4. **异步任务队列**: 处理耗时操作，提高系统响应性
5. **容器化部署**: 支持水平扩展

## 监控与维护

- 配置日志记录系统
- 实现健康检查端点
- 设置性能监控工具
- 制定备份策略
- 准备故障恢复计划
``` 
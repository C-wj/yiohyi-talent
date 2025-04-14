# 家宴菜谱小程序设计文档

## 1. 项目概述

"家宴"是一款家庭菜谱管理与分享的小程序，旨在帮助家庭记录、分享菜谱，并提供点菜、采购清单生成等功能，使家庭饮食管理更加便捷。

### 1.1 核心功能

1. **个人菜谱管理**：用户可创建、编辑和管理个人菜谱
2. **社区菜谱分享**：用户可将个人菜谱分享到社区，也可将社区菜谱保存到个人菜谱中
3. **家庭点菜系统**：记录家庭成员每天各餐想吃的菜品，生成点菜订单
4. **购物清单生成**：根据点菜订单自动生成所需食材的购物清单

### 1.2 目标用户

- 家庭主厨：负责烹饪的家庭成员
- 家庭成员：有参与家庭饮食决策的家庭成员
- 美食爱好者：热爱做菜和分享菜谱的用户

## 2. 系统架构

### 2.1 整体架构

基于TDesign小程序模板框架，采用MVC架构模式：

- **模型层(Model)**：数据管理和业务逻辑
- **视图层(View)**：用户界面和交互组件
- **控制器(Controller)**：处理用户输入并协调模型和视图

### 2.2 目录结构

```
家宴小程序/
├── api/                     # API请求模块
│   ├── recipe.js            # 菜谱相关API
│   ├── order.js             # 点菜订单API
│   ├── shopping.js          # 购物清单API
│   └── community.js         # 社区相关API
├── components/              # 公共组件
│   ├── recipe-card/         # 菜谱卡片组件
│   ├── ingredient-list/     # 食材列表组件
│   ├── step-list/           # 步骤列表组件
│   └── ...
├── custom-tab-bar/          # 自定义底部导航栏
├── mock/                    # 模拟数据
│   ├── recipe/              # 菜谱模拟数据
│   ├── order/               # 订单模拟数据
│   └── ...
├── pages/                   # 页面目录
│   ├── home/                # 首页(社区菜谱)
│   ├── my-recipes/          # 我的菜谱页
│   ├── recipe-detail/       # 菜谱详情页
│   ├── recipe-edit/         # 菜谱编辑页
│   ├── order/               # 点菜系统页
│   ├── shopping-list/       # 购物清单页
│   ├── my/                  # 个人中心页
│   └── ...
├── utils/                   # 公共工具函数
│   ├── recipe.js            # 菜谱相关工具函数
│   ├── order.js             # 订单相关工具函数
│   └── ...
├── app.js                   # 应用入口
├── app.json                 # 应用配置
└── app.wxss                 # 应用样式
```

### 2.3 技术架构

- 前端框架：微信小程序原生框架 + TDesign UI组件库
- 数据管理：小程序云开发(云数据库、云存储)
- 状态管理：全局状态 + 页面状态
- 网络请求：Promise封装的wx.request
- 模拟数据：Mock数据用于开发和测试

## 3. 数据结构设计

### 3.1 菜谱(Recipe)数据结构

```javascript
{
  id: String,                  // 菜谱唯一ID
  title: String,               // 菜谱名称
  coverImage: String,          // 封面图片URL
  description: String,         // 菜谱描述
  tags: Array<String>,         // 标签列表，如"家常菜"、"快手菜"等
  difficulty: Number,          // 难度(1-5)
  prepTime: Number,            // 准备时间(分钟)
  cookTime: Number,            // 烹饪时间(分钟)
  servings: Number,            // 份量(人数)
  
  ingredients: [{              // 食材列表
    name: String,              // 食材名称
    amount: Number,            // 数量
    unit: String,              // 单位(克、个、勺等)
    category: String,          // 分类(肉类、蔬菜类等)
    optional: Boolean          // 是否可选
  }],
  
  steps: [{                    // 步骤列表
    stepNumber: Number,        // 步骤编号
    description: String,       // 步骤描述
    image: String,             // 步骤图片URL(可选)
    tips: String               // 步骤提示(可选)
  }],
  
  tips: Array<String>,         // 烹饪技巧和注意事项
  nutrition: {                 // 营养信息(可选)
    calories: Number,          // 卡路里
    protein: Number,           // 蛋白质(克)
    fat: Number,               // 脂肪(克)
    carbs: Number              // 碳水化合物(克)
  },
  
  creator: {                   // 创建者信息
    userId: String,            // 用户ID
    nickname: String,          // 用户昵称
    avatar: String             // 用户头像
  },
  
  isPublic: Boolean,           // 是否公开分享到社区
  isOrigin: Boolean,           // 是否为原创(false表示从社区导入)
  sourceId: String,            // 若非原创，则为源菜谱ID
  
  stats: {                     // 统计信息
    viewCount: Number,         // 查看次数
    favoriteCount: Number,     // 收藏次数
    commentCount: Number,      // 评论次数
    cookCount: Number          // 做过次数
  },
  
  createdAt: Date,             // 创建时间
  updatedAt: Date              // 更新时间
}
```

### 3.2 点菜订单(Order)数据结构

```javascript
{
  id: String,                  // 订单ID
  familyId: String,            // 家庭ID(支持多家庭)
  date: Date,                  // 日期
  meals: [{                    // 餐次列表
    type: String,              // 餐次类型(早餐、午餐、晚餐)
    dishes: [{                 // 菜品列表
      recipeId: String,        // 菜谱ID
      title: String,           // 菜名
      selectedBy: String,      // 点餐人ID
      servings: Number,        // 份数
      status: String           // 状态(待烹饪、已烹饪)
    }]
  }],
  status: String,              // 订单状态(草稿、已确认、已完成)
  createdAt: Date,             // 创建时间
  updatedAt: Date              // 更新时间
}
```

### 3.3 购物清单(ShoppingList)数据结构

```javascript
{
  id: String,                  // 清单ID
  orderId: String,             // 关联订单ID
  familyId: String,            // 家庭ID
  date: Date,                  // 日期
  items: [{                    // 购物项列表
    name: String,              // 食材名称
    totalAmount: Number,       // 总数量
    unit: String,              // 单位
    category: String,          // 分类
    recipes: [{                // 关联菜谱
      recipeId: String,        // 菜谱ID
      title: String,           // 菜谱名称
      amount: Number           // 需要用量
    }],
    status: String,            // 状态(待购买、已购买)
    note: String               // 备注
  }],
  status: String,              // 清单状态(未完成、已完成)
  createdAt: Date,             // 创建时间
  updatedAt: Date              // 更新时间
}
```

## 4. 功能流程设计

### 4.1 菜谱管理流程

1. **创建菜谱**
   - 用户进入"我的菜谱"页面
   - 点击"新建菜谱"按钮
   - 填写菜谱基本信息(名称、描述、标签等)
   - 添加食材清单(名称、数量、单位)
   - 添加烹饪步骤(步骤描述、图片)
   - 添加烹饪技巧(可选)
   - 填写营养信息(可选)
   - 设置是否公开分享到社区
   - 点击保存完成创建

2. **编辑菜谱**
   - 进入菜谱详情页
   - 点击"编辑"按钮
   - 修改菜谱信息
   - 保存修改

3. **分享菜谱到社区**
   - 在菜谱详情页点击"分享到社区"
   - 确认分享信息
   - 提交分享

4. **从社区导入菜谱**
   - 浏览社区菜谱
   - 点击感兴趣的菜谱查看详情
   - 点击"保存到我的菜谱"按钮
   - 菜谱被复制到个人菜谱库

### 4.2 点菜系统流程

1. **创建点菜单**
   - 进入"点菜"页面
   - 选择日期
   - 为早餐/午餐/晚餐添加菜品
   - 从个人菜谱库中选择菜品
   - 设置每个菜品的份量
   - 保存点菜单

2. **管理点菜单**
   - 查看各日期的点菜单
   - 编辑/删除菜品
   - 标记菜品状态(待烹饪/已烹饪)
   - 确认点菜单生成购物清单

### 4.3 购物清单生成流程

1. **自动生成购物清单**
   - 确认点菜单后自动汇总所需食材
   - 系统自动合并相同食材，计算总量
   - 按食材分类组织购物清单

2. **购物清单管理**
   - 查看购物清单详情
   - 标记已购买的食材
   - 手动添加/编辑/删除食材
   - 查看食材关联的菜谱
   - 导出/分享购物清单

## 5. 页面设计

### 5.1 主要页面

1. **首页(社区菜谱)**
   - 推荐菜谱展示
   - 分类导航
   - 搜索功能
   - 最新/热门菜谱列表

2. **我的菜谱页**
   - 菜谱分类展示
   - 菜谱搜索功能
   - 新建菜谱按钮
   - 菜谱排序和筛选

3. **菜谱详情页**
   - 菜谱基本信息展示
   - 食材清单
   - 步骤详解
   - 烹饪技巧
   - 评论和收藏功能
   - 编辑/分享/导入按钮

4. **点菜系统页**
   - 日期选择器
   - 三餐点菜区域
   - 从我的菜谱选择菜品
   - 点菜统计和确认

5. **购物清单页**
   - 按分类展示食材
   - 食材勾选功能
   - 数量调整功能
   - 添加备注功能
   - 分享清单功能

### 5.2 交互设计原则

1. **简洁直观**：界面简洁，信息层次清晰
2. **一致性**：保持UI和操作的一致性
3. **响应式**：提供即时反馈
4. **预防错误**：设计预防用户错误的机制
5. **高效**：减少操作步骤，提高效率

## 6. API接口设计

### 6.1 菜谱相关接口

- `GET /api/recipes` - 获取菜谱列表
- `GET /api/recipes/:id` - 获取菜谱详情
- `POST /api/recipes` - 创建新菜谱
- `PUT /api/recipes/:id` - 更新菜谱
- `DELETE /api/recipes/:id` - 删除菜谱
- `POST /api/recipes/:id/share` - 分享菜谱到社区
- `POST /api/recipes/:id/import` - 从社区导入菜谱

### 6.2 点菜系统接口

- `GET /api/orders` - 获取点菜订单列表
- `GET /api/orders/:id` - 获取点菜订单详情
- `POST /api/orders` - 创建点菜订单
- `PUT /api/orders/:id` - 更新点菜订单
- `DELETE /api/orders/:id` - 删除点菜订单

### 6.3 购物清单接口

- `GET /api/shopping-lists` - 获取购物清单列表
- `GET /api/shopping-lists/:id` - 获取购物清单详情
- `POST /api/shopping-lists/generate` - 根据订单生成购物清单
- `PUT /api/shopping-lists/:id` - 更新购物清单
- `DELETE /api/shopping-lists/:id` - 删除购物清单

## 7. 项目实施计划

### 7.1 开发阶段

1. **阶段一：基础架构搭建**
   - 搭建项目框架
   - 设计数据库结构
   - 实现基础组件

2. **阶段二：核心功能开发**
   - 菜谱管理功能
   - 社区分享功能
   - 点菜系统功能
   - 购物清单功能

3. **阶段三：UI优化与测试**
   - 界面美化
   - 用户体验优化
   - 功能测试与修复

### 7.2 项目里程碑

- **里程碑1**：完成基础架构和数据结构 - 1周
- **里程碑2**：完成菜谱管理和社区分享功能 - 2周
- **里程碑3**：完成点菜系统功能 - 1周
- **里程碑4**：完成购物清单功能 - 1周
- **里程碑5**：完成UI优化与测试 - 1周

## 8. 未来扩展计划

1. **智能推荐**：基于用户喜好推荐菜谱
2. **营养分析**：提供菜谱和饮食的营养分析
3. **季节性菜谱**：根据季节推荐应季食材和菜谱
4. **食材价格跟踪**：监控食材价格波动
5. **多家庭协作**：支持多个家庭成员协作管理菜谱和点菜
6. **视频教程**：支持视频形式的烹饪教程 
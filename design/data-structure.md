# 家宴菜谱小程序数据结构设计

## 1. 数据模型概述

家宴菜谱小程序主要包含以下核心数据模型：

1. **用户(User)**：应用用户信息
2. **菜谱(Recipe)**：菜谱详细信息
3. **点菜订单(Order)**：家庭点菜记录
4. **购物清单(ShoppingList)**：购物清单信息
5. **家庭(Family)**：家庭群组信息

本文档详细说明各数据模型的结构设计，重点关注菜谱数据模型的设计及其与其他模型的关系。

## 2. 菜谱(Recipe)数据模型详解

### 2.1 基本信息字段

```javascript
{
  // 基本标识
  id: String,                  // 菜谱唯一ID，系统生成
  title: String,               // 菜谱名称，必填
  coverImage: String,          // 封面图片URL，必填
  description: String,         // 菜谱描述，可选
  
  // 菜谱分类信息
  tags: Array<String>,         // 标签列表，如"家常菜"、"快手菜"等
  category: String,            // 主分类，如"荤菜"、"素菜"、"汤品"等
  cuisine: String,             // 菜系，如"川菜"、"粤菜"等
  
  // 烹饪信息
  difficulty: Number,          // 难度(1-5)，1最简单，5最复杂
  prepTime: Number,            // 准备时间(分钟)
  cookTime: Number,            // 烹饪时间(分钟)
  totalTime: Number,           // 总时间(分钟)，prepTime + cookTime
  servings: Number,            // 份量(人数)
  
  // 创建者信息
  creator: {
    userId: String,            // 用户ID
    nickname: String,          // 用户昵称
    avatar: String             // 用户头像
  },
  
  // 状态标记
  isPublic: Boolean,           // 是否公开分享到社区
  isOrigin: Boolean,           // 是否为原创(false表示从社区导入)
  sourceId: String,            // 若非原创，则为源菜谱ID
  status: String,              // 状态：'draft'(草稿),'published'(已发布),'deleted'(已删除)
  
  // 统计信息
  stats: {
    viewCount: Number,         // 查看次数
    favoriteCount: Number,     // 收藏次数
    commentCount: Number,      // 评论次数
    cookCount: Number,         // 做过次数
    ratingAvg: Number,         // 平均评分(1-5)
    ratingCount: Number        // 评分人数
  },
  
  // 时间信息
  createdAt: Date,             // 创建时间
  updatedAt: Date              // 更新时间
}
```

### 2.2 食材(Ingredient)子模型

```javascript
ingredients: [{
  id: String,                  // 食材条目ID
  name: String,                // 食材名称(必填)
  amount: Number,              // 数量(必填)
  unit: String,                // 单位(克、个、勺等)
  category: String,            // 分类(肉类、蔬菜类等)
  optional: Boolean,           // 是否可选，默认false
  substitutes: [{              // 替代食材
    name: String,              // 替代食材名称
    amount: Number,            // 替代数量
    unit: String               // 替代单位
  }],
  note: String                 // 备注(如处理方式等)
}]
```

### 2.3 步骤(Step)子模型

```javascript
steps: [{
  stepNumber: Number,          // 步骤编号(必填)
  description: String,         // 步骤描述(必填)
  image: String,               // 步骤图片URL(可选)
  duration: Number,            // 预计耗时(分钟，可选)
  tips: String,                // 步骤提示(可选)
  ingredients: [String],       // 该步骤使用的食材ID列表
  tools: [String]              // 该步骤使用的厨具列表
}]
```

### 2.4 营养(Nutrition)子模型

```javascript
nutrition: {
  calories: Number,            // 热量(千卡)
  protein: Number,             // 蛋白质(克)
  fat: Number,                 // 脂肪(克)
  carbs: Number,               // 碳水化合物(克)
  fiber: Number,               // 膳食纤维(克)
  sugar: Number,               // 糖(克)
  sodium: Number,              // 钠(毫克)
  cholesterol: Number,         // 胆固醇(毫克)
  vitamins: {                  // 维生素含量
    A: Number,                 // 维生素A(IU)
    C: Number,                 // 维生素C(毫克)
    // 其他维生素...
  },
  minerals: {                  // 矿物质含量
    calcium: Number,           // 钙(毫克)
    iron: Number,              // 铁(毫克)
    // 其他矿物质...
  },
  source: String               // 营养数据来源
}
```

### 2.5 附加信息

```javascript
tips: [String],                // 烹饪技巧和注意事项
story: String,                 // 菜谱背后的故事
occasion: [String],            // 适合的场合，如"家庭聚餐"、"节日"
season: [String],              // 适合的季节
allergens: [String],           // 过敏原警告，如"花生"、"海鲜"
video: {                       // 视频教程
  url: String,                 // 视频地址
  duration: Number,            // 视频时长(秒)
  cover: String                // 视频封面图
},
comments: [{                   // 评论列表(或使用单独集合)
  userId: String,              // 评论用户ID
  content: String,             // 评论内容
  rating: Number,              // 评分(1-5)
  images: [String],            // 评论图片
  createdAt: Date              // 评论时间
}]
```

## 3. 点菜订单(Order)数据模型

```javascript
{
  id: String,                  // 订单ID
  familyId: String,            // 家庭ID(支持多家庭)
  creatorId: String,           // 创建者ID
  title: String,               // 订单标题，如"周末家宴"
  date: Date,                  // 日期
  
  meals: [{                    // 餐次列表
    type: String,              // 餐次类型:'breakfast','lunch','dinner','other'
    time: String,              // 用餐时间，如"12:00"
    dishes: [{                 // 菜品列表
      recipeId: String,        // 菜谱ID
      title: String,           // 菜名
      selectedBy: String,      // 点餐人ID
      selectedByName: String,  // 点餐人姓名
      servings: Number,        // 份数
      status: String,          // 状态:'pending','cooking','completed'
      note: String             // 备注，如"少放辣"
    }]
  }],
  
  guestCount: Number,          // 用餐人数
  specialNeeds: String,        // 特殊需求，如"有儿童"
  status: String,              // 订单状态:'draft','confirmed','completed'
  shoppingListId: String,      // 关联的购物清单ID
  
  createdAt: Date,             // 创建时间
  updatedAt: Date,             // 更新时间
  confirmedAt: Date            // 确认时间
}
```

## 4. 购物清单(ShoppingList)数据模型

```javascript
{
  id: String,                  // 清单ID
  orderId: String,             // 关联订单ID
  familyId: String,            // 家庭ID
  title: String,               // 清单标题
  date: Date,                  // 日期
  
  items: [{                    // 购物项列表
    id: String,                // 项目ID
    name: String,              // 食材名称
    totalAmount: Number,       // 总数量
    unit: String,              // 单位
    category: String,          // 分类
    priority: String,          // 优先级:'high','medium','low'
    recipes: [{                // 关联菜谱
      recipeId: String,        // 菜谱ID
      title: String,           // 菜谱名称
      amount: Number,          // 需要用量
      unit: String             // 单位
    }],
    status: String,            // 状态:'pending','purchased'
    purchasedBy: String,       // 购买人ID
    purchasedAt: Date,         // 购买时间
    price: Number,             // 价格
    note: String               // 备注
  }],
  
  totalCost: Number,           // 总花费
  status: String,              // 清单状态:'active','completed'
  completedAt: Date,           // 完成时间
  
  createdAt: Date,             // 创建时间
  updatedAt: Date              // 更新时间
}
```

## 5. 用户(User)数据模型

```javascript
{
  id: String,                  // 用户ID
  openid: String,              // 微信openid
  unionid: String,             // 微信unionid(如适用)
  
  profile: {
    nickname: String,          // 昵称
    avatar: String,            // 头像URL
    gender: Number,            // 性别: 0未知，1男，2女
    bio: String                // 个人简介
  },
  
  preferences: {
    dietary: [String],         // 饮食偏好，如"素食","低脂"
    allergies: [String],       // 过敏原，如"花生","海鲜"
    favoriteCuisines: [String],// 喜好的菜系
    dislikedIngredients: [String] // 不喜欢的食材
  },
  
  stats: {
    recipeCount: Number,       // 创建的菜谱数
    favoriteCount: Number,     // 收藏的菜谱数
    orderCount: Number,        // 创建的点菜订单数
    followersCount: Number,    // 粉丝数
    followingCount: Number     // 关注数
  },
  
  families: [String],          // 所属家庭ID列表
  
  settings: {
    notification: Boolean,     // 通知设置
    privacy: String,           // 隐私设置:'public','friends','private'
    theme: String              // 主题设置:'light','dark'
  },
  
  createdAt: Date,             // 创建时间
  lastLoginAt: Date            // 最后登录时间
}
```

## 6. 家庭(Family)数据模型

```javascript
{
  id: String,                  // 家庭ID
  name: String,                // 家庭名称
  avatar: String,              // 家庭头像URL
  creator: String,             // 创建者ID
  
  members: [{                  // 成员列表
    userId: String,            // 用户ID
    nickname: String,          // 家庭内昵称
    role: String,              // 角色:'admin','member','guest'
    joinedAt: Date             // 加入时间
  }],
  
  settings: {
    mealReminder: Boolean,     // 用餐提醒
    shoppingDay: String,       // 常规购物日，如"周六"
    defaultServings: Number    // 默认份量
  },
  
  createdAt: Date,             // 创建时间
  updatedAt: Date              // 更新时间
}
```

## 7. 数据关系设计

### 7.1 数据关系图

```
User(1) ----< Recipe(n)        # 用户创建多个菜谱
User(1) ----< Order(n)         # 用户创建多个点菜订单
User(n) >---- Family(m)        # 用户可属于多个家庭，家庭有多个用户

Recipe(1) ----< OrderDish(n)   # 一个菜谱可以出现在多个点菜项中

Order(1) ----< ShoppingList(1) # 一个点菜订单生成一个购物清单
Family(1) ----< Order(n)       # 一个家庭有多个点菜订单
```

### 7.2 索引设计

为提高查询效率，建议在以下字段上建立索引：

1. Recipe表：
   - creator.userId（按创建者查询菜谱）
   - tags（按标签查询菜谱）
   - isPublic（查询公开菜谱）
   - status（过滤菜谱状态）

2. Order表：
   - familyId（按家庭查询订单）
   - date（按日期查询订单）
   - status（过滤订单状态）

3. ShoppingList表：
   - orderId（根据订单查询购物清单）
   - familyId（按家庭查询购物清单）
   - status（过滤购物清单状态）

## 8. 数据存储方案

考虑微信小程序的特点，推荐以下存储方案：

### 8.1 云数据库

使用微信小程序云开发的云数据库，创建以下集合：
- recipes
- orders
- shopping_lists
- users
- families

### 8.2 云存储

用于存储用户上传的图片资源：
- 菜谱封面图
- 步骤图片
- 用户头像
- 评论图片

### 8.3 数据安全规则

1. **菜谱数据**：
   - 公开菜谱所有用户可读
   - 私有菜谱仅创建者可读写
   - 导入菜谱时创建新记录，保留源菜谱ID

2. **点菜订单**：
   - 仅家庭成员可读写
   - 可设置部分字段给指定成员修改权限

3. **购物清单**：
   - 仅家庭成员可读写
   - 可导出分享给临时用户（仅查看权限）

## 9. 数据迁移和备份策略

1. **定期备份**：
   - 每日自动备份菜谱数据
   - 每周全量备份所有数据

2. **数据导出**：
   - 提供菜谱数据导出功能，支持JSON格式
   - 提供购物清单导出功能，支持CSV格式

3. **版本控制**：
   - 菜谱数据保留修改历史记录
   - 点菜订单保存确认前后的版本
   
## 10. 数据扩展性设计

为了保证系统的可扩展性，数据结构设计考虑了以下几点：

1. **模块化设计**：
   - 将大型对象分解为子模块
   - 使用引用关系而非嵌入式文档（适当情况）

2. **可扩展字段**：
   - 添加metadata字段存储自定义属性
   - 预留扩展接口字段

3. **版本控制**：
   - 在架构中包含schemaVersion字段
   - 支持向前兼容的设计

通过这种设计，数据模型既能满足当前需求，又能适应未来的功能扩展，如多设备同步、数据分析和智能推荐等高级功能。 
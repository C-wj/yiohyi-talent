# 家宴菜谱小程序 - 页面操作与API设计

## 1. 页面操作清单

### 1.1 首页 (社区菜谱)

**主要操作：**
- 浏览推荐菜谱
- 按分类浏览菜谱
- 搜索菜谱
- 查看热门/最新菜谱
- 点击菜谱进入详情

**交互细节：**
- 上拉加载更多菜谱
- 下拉刷新菜谱列表
- 点击分类标签筛选菜谱
- 输入关键词搜索菜谱

### 1.2 我的菜谱页

**主要操作：**
- 查看个人创建/收藏的菜谱
- 创建新菜谱
- 搜索个人菜谱
- 编辑/删除菜谱
- 按标签/分类筛选菜谱

**交互细节：**
- 长按菜谱卡片显示操作菜单
- 点击筛选按钮展示筛选选项
- 点击排序按钮切换排序方式
- 点击"+"按钮创建新菜谱

### 1.3 菜谱详情页

**主要操作：**
- 查看菜谱基本信息
- 查看食材清单
- 查看烹饪步骤
- 收藏/取消收藏菜谱
- 分享菜谱
- 编辑菜谱(仅创建者)
- 导入到个人菜谱(社区菜谱)
- 查看/发表评论

**交互细节：**
- 食材列表可展开/收起
- 步骤可左右滑动查看
- 点击步骤图片放大查看
- 点击"加入菜单"快速添加到点菜系统

### 1.4 菜谱编辑页

**主要操作：**
- 编辑基本信息(名称、描述等)
- 添加/编辑/删除食材
- 添加/编辑/删除步骤
- 添加/编辑步骤图片
- 选择菜谱分类和标签
- 设置烹饪参数(难度、时间等)
- 设置是否公开分享

**交互细节：**
- 拖拽排序食材和步骤
- 上传图片时可裁剪调整
- 表单验证确保必填项完整
- 自动保存草稿功能

### 1.5 点菜系统页

**主要操作：**
- 选择日期查看/创建点菜单
- 为早/午/晚餐添加菜品
- 从个人菜谱库选择菜品
- 设置菜品份量
- 添加/编辑点菜备注
- 邀请家人协作点菜
- 确认点菜单
- 生成购物清单

**交互细节：**
- 日历视图展示已有点菜日期
- 餐次区域可折叠/展开
- 菜品选择支持搜索和分类筛选
- 实时同步协作者的点菜操作

### 1.6 购物清单页

**主要操作：**
- 查看按分类组织的食材列表
- 标记已购买食材
- 添加额外食材
- 调整食材数量
- 删除不需要的食材
- 查看食材关联的菜谱
- 分享购物清单
- 导出购物清单
- 完成购物标记

**交互细节：**
- 点击食材显示来源菜谱
- 左滑食材显示编辑/删除选项
- 一键标记全部/分类已购买
- 按购买状态筛选显示

### 1.7 个人中心页

**主要操作：**
- 查看/编辑个人信息
- 管理家庭成员
- 创建/加入家庭
- 查看统计数据
- 设置偏好(口味偏好、饮食限制等)
- 系统设置(通知、隐私等)
- 提交反馈

**交互细节：**
- 点击头像编辑个人信息
- 滑动切换不同家庭
- 长按家庭成员显示管理选项
- 统计数据以图表形式展示

## 2. MongoDB数据结构设计

### 2.1 用户集合 (users)

```javascript
{
  _id: ObjectId,               // MongoDB自动生成的ID
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
  families: [String],          // 所属家庭ID列表(引用families集合)
  settings: {
    notification: Boolean,     // 通知设置
    privacy: String,           // 隐私设置:'public','friends','private'
    theme: String              // 主题设置:'light','dark'
  },
  createdAt: Date,             // 创建时间
  lastLoginAt: Date,           // 最后登录时间
  updatedAt: Date              // 更新时间
}
```

### 2.2 菜谱集合 (recipes)

```javascript
{
  _id: ObjectId,               // MongoDB自动生成的ID
  title: String,               // 菜谱名称
  coverImage: String,          // 封面图片URL
  description: String,         // 菜谱描述
  tags: [String],              // 标签列表，如"家常菜"、"快手菜"等
  category: String,            // 主分类，如"荤菜"、"素菜"、"汤品"等
  cuisine: String,             // 菜系，如"川菜"、"粤菜"等
  difficulty: Number,          // 难度(1-5)
  prepTime: Number,            // 准备时间(分钟)
  cookTime: Number,            // 烹饪时间(分钟)
  totalTime: Number,           // 总时间(分钟)
  servings: Number,            // 份量(人数)
  
  creator: {
    userId: String,            // 用户ID (引用users集合)
    nickname: String,          // 用户昵称
    avatar: String             // 用户头像
  },
  
  ingredients: [{
    name: String,              // 食材名称
    amount: Number,            // 数量
    unit: String,              // 单位(克、个、勺等)
    category: String,          // 分类(肉类、蔬菜类等)
    optional: Boolean,         // 是否可选
    substitutes: [{            // 替代食材
      name: String,            // 替代食材名称
      amount: Number,          // 替代数量
      unit: String             // 替代单位
    }],
    note: String               // 备注(如处理方式等)
  }],
  
  steps: [{
    stepNumber: Number,        // 步骤编号
    description: String,       // 步骤描述
    image: String,             // 步骤图片URL(可选)
    duration: Number,          // 预计耗时(分钟，可选)
    tips: String,              // 步骤提示(可选)
  }],
  
  nutrition: {
    calories: Number,          // 热量(千卡)
    protein: Number,           // 蛋白质(克)
    fat: Number,               // 脂肪(克)
    carbs: Number,             // 碳水化合物(克)
    fiber: Number,             // 膳食纤维(克)
    sugar: Number,             // 糖(克)
    sodium: Number,            // 钠(毫克)
    source: String             // 营养数据来源
  },
  
  tips: [String],              // 烹饪技巧和注意事项
  
  isPublic: Boolean,           // 是否公开分享到社区
  isOrigin: Boolean,           // 是否为原创(false表示从社区导入)
  sourceId: String,            // 若非原创，则为源菜谱ID
  status: String,              // 状态:'draft','published','deleted'
  
  stats: {
    viewCount: Number,         // 查看次数
    favoriteCount: Number,     // 收藏次数
    commentCount: Number,      // 评论次数
    cookCount: Number,         // 做过次数
    ratingAvg: Number,         // 平均评分(1-5)
    ratingCount: Number        // 评分人数
  },
  
  createdAt: Date,             // 创建时间
  updatedAt: Date              // 更新时间
}
```

### 2.3 评论集合 (comments)

```javascript
{
  _id: ObjectId,               // MongoDB自动生成的ID
  recipeId: String,            // 关联菜谱ID (引用recipes集合)
  userId: String,              // 评论用户ID (引用users集合)
  content: String,             // 评论内容
  rating: Number,              // 评分(1-5)
  images: [String],            // 评论图片URL数组
  likes: Number,               // 点赞数
  parentId: String,            // 父评论ID(用于回复功能，可选)
  createdAt: Date,             // 创建时间
  updatedAt: Date              // 更新时间
}
```

### 2.4 菜单计划集合 (menu_plans)

```javascript
{
  _id: ObjectId,               // MongoDB自动生成的ID
  name: String,                // 菜单计划名称
  familyId: String,            // 家庭ID (引用families集合)
  creatorId: String,           // 创建者ID (引用users集合)
  date: Date,                  // 日期
  
  meals: [{
    type: String,              // 餐次类型:'breakfast','lunch','dinner','other'
    time: String,              // 用餐时间，如"12:00"
    dishes: [{
      recipeId: String,        // 菜谱ID (引用recipes集合)
      title: String,           // 菜名
      selectedBy: String,      // 点餐人ID (引用users集合)
      selectedByName: String,  // 点餐人姓名
      servings: Number,        // 份数
      status: String,          // 状态:'pending','cooking','completed'
      note: String             // 备注，如"少放辣"
    }]
  }],
  
  guestCount: Number,          // 用餐人数
  specialNeeds: String,        // 特殊需求，如"有儿童"
  status: String,              // 状态:'draft','confirmed','completed'
  shoppingListId: String,      // 关联的购物清单ID (引用shopping_lists集合)
  
  collaborators: [{
    userId: String,            // 用户ID (引用users集合)
    role: String,              // 角色:'admin','editor','viewer'
    joinedAt: Date             // 加入时间
  }],
  
  createdAt: Date,             // 创建时间
  updatedAt: Date,             // 更新时间
  confirmedAt: Date            // 确认时间
}
```

### 2.5 购物清单集合 (shopping_lists)

```javascript
{
  _id: ObjectId,               // MongoDB自动生成的ID
  planId: String,              // 关联菜单计划ID (引用menu_plans集合)
  familyId: String,            // 家庭ID (引用families集合)
  name: String,                // 清单名称
  date: Date,                  // 日期
  
  items: [{
    name: String,              // 食材名称
    totalAmount: Number,       // 总数量
    unit: String,              // 单位
    category: String,          // 分类
    priority: String,          // 优先级:'high','medium','low'
    sources: [{                // 来源菜谱
      recipeId: String,        // 菜谱ID (引用recipes集合)
      title: String,           // 菜谱名称
      amount: Number,          // 需要用量
      unit: String             // 单位
    }],
    checked: Boolean,          // 是否已购买
    purchasedBy: String,       // 购买人ID (引用users集合)
    purchasedAt: Date,         // 购买时间
    price: Number,             // 价格
    note: String               // 备注
  }],
  
  totalCost: Number,           // 总花费
  status: String,              // 状态:'active','completed'
  
  sharedWith: [{
    userId: String,            // 用户ID (引用users集合)
    permissions: String,       // 权限:'edit','view'
    sharedAt: Date             // 分享时间
  }],
  
  createdAt: Date,             // 创建时间
  updatedAt: Date,             // 更新时间
  completedAt: Date            // 完成时间
}
```

### 2.6 家庭集合 (families)

```javascript
{
  _id: ObjectId,               // MongoDB自动生成的ID
  name: String,                // 家庭名称
  avatar: String,              // 家庭头像URL
  creator: String,             // 创建者ID (引用users集合)
  
  members: [{
    userId: String,            // 用户ID (引用users集合)
    nickname: String,          // 家庭内昵称
    role: String,              // 角色:'admin','member','guest'
    joinedAt: Date             // 加入时间
  }],
  
  settings: {
    mealReminder: Boolean,     // 用餐提醒
    shoppingDay: String,       // 常规购物日，如"周六"
    defaultServings: Number,   // 默认份量
    dietaryRestrictions: [String] // 饮食限制
  },
  
  invitations: [{              // 邀请记录
    code: String,              // 邀请码
    expiresAt: Date,           // 过期时间
    createdBy: String,         // 创建者ID (引用users集合)
    usedBy: String,            // 使用者ID (引用users集合)
    usedAt: Date               // 使用时间
  }],
  
  createdAt: Date,             // 创建时间
  updatedAt: Date              // 更新时间
}
```

### 2.7 收藏集合 (favorites)

```javascript
{
  _id: ObjectId,               // MongoDB自动生成的ID
  userId: String,              // 用户ID (引用users集合)
  recipeId: String,            // 菜谱ID (引用recipes集合)
  createdAt: Date              // 收藏时间
}
```

### 2.8 索引设计

为提高查询效率，建议在以下字段上建立索引：

1. **users集合**:
   - `openid` (唯一索引)
   - `families` (多键索引)

2. **recipes集合**:
   - `creator.userId` (常用于查询用户创建的菜谱)
   - `tags` (多键索引，常用于标签筛选)
   - `isPublic`和`status`的组合索引 (常用于筛选公开且已发布菜谱)

3. **menu_plans集合**:
   - `familyId` (常用于查询家庭菜单)
   - `date` (常用于日期查询)
   - `creatorId` (常用于查询用户创建的菜单)

4. **shopping_lists集合**:
   - `planId` (用于关联菜单计划)
   - `familyId` (用于家庭查询)

5. **favorites集合**:
   - `userId`和`recipeId`的组合索引 (唯一索引，防止重复收藏)
   - `userId` (用于查询用户收藏)

## 3. API接口文档

### 3.1 用户认证与管理

#### 用户登录/注册
- **接口**: `/api/v1/auth/login`
- **方法**: POST
- **功能**: 微信登录并获取用户信息，首次登录自动注册
- **参数**: 
  - `code`: 微信临时登录凭证
- **返回**: 用户信息、登录态token
- **MongoDB操作**: 在users集合中查询或创建用户文档

#### 获取用户信息
- **接口**: `/api/v1/users/profile`
- **方法**: GET
- **功能**: 获取当前用户详细信息
- **参数**: 无 (使用登录态)
- **返回**: 用户详细信息
- **MongoDB操作**: 根据用户ID查询users集合

#### 更新用户信息
- **接口**: `/api/v1/users/profile`
- **方法**: PUT
- **功能**: 更新用户基础信息
- **参数**: `nickname`, `avatar_url`, `gender` 等
- **返回**: 更新后的用户信息
- **MongoDB操作**: 更新users集合中的profile字段

#### 更新用户偏好
- **接口**: `/api/v1/users/preferences`
- **方法**: PUT
- **功能**: 更新用户口味偏好、饮食限制等
- **参数**: `taste_preferences`, `dietary_restrictions` 等
- **返回**: 更新后的用户偏好
- **MongoDB操作**: 更新users集合中的preferences字段

### 3.2 家庭管理

#### 创建家庭
- **接口**: `/api/v1/families`
- **方法**: POST
- **功能**: 创建新家庭
- **参数**: `name`, `meal_preferences` 等
- **返回**: 创建的家庭信息
- **MongoDB操作**: 
  1. 在families集合中创建新文档
  2. 更新users集合中的families数组

#### 获取家庭信息
- **接口**: `/api/v1/families/{family_id}`
- **方法**: GET
- **功能**: 获取家庭详细信息
- **参数**: 无
- **返回**: 家庭详细信息
- **MongoDB操作**: 根据ID查询families集合

#### 添加家庭成员
- **接口**: `/api/v1/families/{family_id}/members`
- **方法**: POST
- **功能**: 添加新家庭成员
- **参数**: `user_id`, `nickname`, `role`
- **返回**: 更新后的家庭成员列表
- **MongoDB操作**: 
  1. 更新families集合中的members数组
  2. 更新users集合中的families数组

#### 生成家庭邀请码
- **接口**: `/api/v1/families/{family_id}/invitation`
- **方法**: POST
- **功能**: 生成邀请链接或邀请码
- **参数**: `expires_in` (过期时间)
- **返回**: 邀请链接或邀请码
- **MongoDB操作**: 在families集合中添加新的邀请记录

### 3.3 菜谱管理

#### 创建菜谱
- **接口**: `/api/v1/recipes`
- **方法**: POST
- **功能**: 创建新菜谱
- **参数**: `title`, `description`, `ingredients`, `steps` 等
- **返回**: 创建的菜谱信息
- **MongoDB操作**: 在recipes集合中创建新文档

#### 获取菜谱详情
- **接口**: `/api/v1/recipes/{recipe_id}`
- **方法**: GET
- **功能**: 获取菜谱详细信息
- **参数**: 无
- **返回**: 菜谱详细信息
- **MongoDB操作**: 
  1. 根据ID查询recipes集合
  2. 增加recipes集合中的viewCount字段值

#### 更新菜谱
- **接口**: `/api/v1/recipes/{recipe_id}`
- **方法**: PUT
- **功能**: 更新菜谱信息
- **参数**: `title`, `description`, `ingredients`, `steps` 等
- **返回**: 更新后的菜谱信息
- **MongoDB操作**: 更新recipes集合中的对应文档

#### 收藏菜谱
- **接口**: `/api/v1/recipes/{recipe_id}/favorite`
- **方法**: POST
- **功能**: 收藏菜谱
- **参数**: 无
- **返回**: 操作结果
- **MongoDB操作**: 
  1. 在favorites集合中创建新文档
  2. 更新recipes集合中的favoriteCount字段值
  3. 更新users集合中的favoriteCount字段值

#### 社区菜谱搜索
- **接口**: `/api/v1/recipes/search`
- **方法**: GET
- **功能**: 搜索社区菜谱
- **参数**: `keyword`, `tags`, `cuisine_type`, `difficulty` 等
- **返回**: 菜谱列表及分页信息
- **MongoDB操作**: 在recipes集合中使用$text索引或正则表达式搜索

### 3.4 点菜系统

#### 创建菜单计划
- **接口**: `/api/v1/menu-plans`
- **方法**: POST
- **功能**: 创建新的菜单计划
- **参数**: `name`, `date`, `meal_type`, `servings` 等
- **返回**: 创建的菜单计划信息
- **MongoDB操作**: 在menu_plans集合中创建新文档

#### 添加菜品到菜单
- **接口**: `/api/v1/menu-plans/{plan_id}/dishes`
- **方法**: POST
- **功能**: 向菜单添加菜品
- **参数**: `recipe_id`, `quantity`, `notes` 等
- **返回**: 添加的菜品信息
- **MongoDB操作**: 更新menu_plans集合中的meals.dishes数组

#### 获取家庭的菜单计划
- **接口**: `/api/v1/menu-plans/by-family/{family_id}`
- **方法**: GET
- **功能**: 获取指定家庭的菜单计划
- **参数**: `page`, `limit`, `status`
- **返回**: 菜单计划列表及分页信息
- **MongoDB操作**: 根据familyId查询menu_plans集合

### 3.5 购物清单

#### 从菜单生成购物清单
- **接口**: `/api/v1/shopping-lists/generate`
- **方法**: POST
- **功能**: 基于选定菜单生成购物清单
- **参数**: `plan_ids`, `name`
- **返回**: 生成的购物清单信息
- **MongoDB操作**: 
  1. 查询menu_plans集合获取相关菜单
  2. 查询recipes集合获取所需食材
  3. 在shopping_lists集合中创建新文档

#### 更新购物项目
- **接口**: `/api/v1/shopping-lists/{list_id}/items/{item_id}`
- **方法**: PUT
- **功能**: 更新购物项目信息
- **参数**: `checked`, `amount`, `notes` 等
- **返回**: 更新后的购物项目信息
- **MongoDB操作**: 更新shopping_lists集合中的items数组中的特定项目

#### 批量更新购物项目状态
- **接口**: `/api/v1/shopping-lists/{list_id}/items/batch-update`
- **方法**: PUT
- **功能**: 批量更新多个购物项目的状态
- **参数**: `item_ids`, `checked`
- **返回**: 更新结果
- **MongoDB操作**: 更新shopping_lists集合中的多个items的checked状态

### 3.6 智能食材合并

#### 食材智能识别
- **接口**: `/api/v1/ingredients/recognize`
- **方法**: POST
- **功能**: 智能识别食材名称、分类和单位
- **参数**: `ingredient_text`
- **返回**: 识别结果
- **MongoDB操作**: 可能需要查询已有食材数据库进行匹配

#### 食材合并预览
- **接口**: `/api/v1/ingredients/merge-preview`
- **方法**: POST
- **功能**: 预览多个食材合并结果
- **参数**: `ingredients` (食材列表)
- **返回**: 合并后的食材列表
- **MongoDB操作**: 无数据库操作，纯算法处理

### 3.7 辅助接口

#### 文件上传
- **接口**: `/api/v1/upload`
- **方法**: POST
- **功能**: 上传图片或其他文件
- **参数**: `file`, `type` (recipe/avatar/step)
- **返回**: 上传后的文件URL
- **MongoDB操作**: 无数据库操作，但需要存储文件到云存储

#### 获取季节性推荐
- **接口**: `/api/v1/seasonal-recommendations`
- **方法**: GET
- **功能**: 获取当前季节的食材和菜谱推荐
- **参数**: `season` (可选，默认为当前季节)
- **返回**: 季节性推荐信息
- **MongoDB操作**: 查询recipes集合中适合当前季节的菜谱

#### 用户反馈提交
- **接口**: `/api/v1/feedback`
- **方法**: POST
- **功能**: 提交用户反馈或问题
- **参数**: `content`, `contact_info`, `type`
- **返回**: 提交结果
- **MongoDB操作**: 可能需要创建feedback集合存储用户反馈

## 4. 数据库索引与性能优化

### 4.1 索引策略

MongoDB中使用适当的索引可以显著提高查询效率。建议创建以下索引：

```javascript
// users集合索引
db.users.createIndex({ "openid": 1 }, { unique: true })
db.users.createIndex({ "families": 1 })

// recipes集合索引
db.recipes.createIndex({ "creator.userId": 1 })
db.recipes.createIndex({ "tags": 1 })
db.recipes.createIndex({ "isPublic": 1, "status": 1 })
db.recipes.createIndex({ "title": "text", "description": "text" }) // 文本搜索

// menu_plans集合索引
db.menu_plans.createIndex({ "familyId": 1 })
db.menu_plans.createIndex({ "date": 1 })
db.menu_plans.createIndex({ "creatorId": 1 })

// shopping_lists集合索引
db.shopping_lists.createIndex({ "planId": 1 })
db.shopping_lists.createIndex({ "familyId": 1 })

// favorites集合索引
db.favorites.createIndex({ "userId": 1, "recipeId": 1 }, { unique: true })
db.favorites.createIndex({ "userId": 1 })
```

### 4.2 查询优化

1. **使用投影限制返回字段**
   ```javascript
   db.recipes.find({}, { title: 1, coverImage: 1, difficulty: 1 })
   ```

2. **分页查询优化**
   ```javascript
   db.recipes.find({}).skip(20).limit(10)
   ```

3. **使用聚合管道处理复杂查询**
   ```javascript
   db.recipes.aggregate([
     { $match: { isPublic: true, status: "published" } },
     { $sort: { createdAt: -1 } },
     { $limit: 10 },
     { $lookup: { from: "users", localField: "creator.userId", foreignField: "_id", as: "creator_details" } }
   ])
   ```

### 4.3 数据库性能监控

定期监控以下指标：
- 查询执行时间
- 索引使用情况
- 数据库大小和增长率
- 连接数及连接池使用情况

## 5. 错误处理与状态码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/登录过期 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 500 | 服务器内部错误 |

## 6. 响应格式标准

所有API接口响应都遵循以下统一格式：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    // 具体数据
  }
}
```

分页数据格式：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "list": [],
    "pagination": {
      "total": 100,
      "page": 1,
      "limit": 10,
      "pages": 10
    }
  }
}
``` 
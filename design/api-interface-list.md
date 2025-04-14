# 家宴菜谱小程序 - API接口清单

本文档列出了家宴菜谱小程序的所有后端API接口，供开发团队参考。

## 1. 用户认证与管理接口

1. **用户登录/注册**
   - 接口: `/api/v1/auth/login`
   - 方法: POST
   - 功能: 微信登录并获取用户信息，首次登录自动注册
   - 参数: `code` (微信临时登录凭证)
   - 返回: 用户信息、登录态token

2. **获取用户信息**
   - 接口: `/api/v1/users/profile`
   - 方法: GET
   - 功能: 获取当前用户详细信息
   - 参数: 无 (使用登录态)
   - 返回: 用户详细信息

3. **更新用户信息**
   - 接口: `/api/v1/users/profile`
   - 方法: PUT
   - 功能: 更新用户基础信息
   - 参数: `nickname`, `avatar_url`, `gender` 等
   - 返回: 更新后的用户信息

4. **更新用户偏好**
   - 接口: `/api/v1/users/preferences`
   - 方法: PUT
   - 功能: 更新用户口味偏好、饮食限制等
   - 参数: `taste_preferences`, `dietary_restrictions` 等
   - 返回: 更新后的用户偏好

5. **获取用户统计数据**
   - 接口: `/api/v1/users/statistics`
   - 方法: GET
   - 功能: 获取用户相关统计数据
   - 参数: 无
   - 返回: 用户统计数据

## 2. 家庭管理接口

1. **创建家庭**
   - 接口: `/api/v1/families`
   - 方法: POST
   - 功能: 创建新家庭
   - 参数: `name`, `meal_preferences` 等
   - 返回: 创建的家庭信息

2. **获取家庭信息**
   - 接口: `/api/v1/families/{family_id}`
   - 方法: GET
   - 功能: 获取家庭详细信息
   - 参数: 无
   - 返回: 家庭详细信息

3. **更新家庭信息**
   - 接口: `/api/v1/families/{family_id}`
   - 方法: PUT
   - 功能: 更新家庭基本信息
   - 参数: `name`, `meal_preferences` 等
   - 返回: 更新后的家庭信息

4. **添加家庭成员**
   - 接口: `/api/v1/families/{family_id}/members`
   - 方法: POST
   - 功能: 添加新家庭成员
   - 参数: `user_id`, `nickname`, `role`
   - 返回: 更新后的家庭成员列表

5. **移除家庭成员**
   - 接口: `/api/v1/families/{family_id}/members/{user_id}`
   - 方法: DELETE
   - 功能: 移除家庭成员
   - 参数: 无
   - 返回: 操作结果

6. **生成家庭邀请码**
   - 接口: `/api/v1/families/{family_id}/invitation`
   - 方法: POST
   - 功能: 生成邀请链接或邀请码
   - 参数: `expires_in` (过期时间)
   - 返回: 邀请链接或邀请码

7. **获取用户所有家庭**
   - 接口: `/api/v1/families/mine`
   - 方法: GET
   - 功能: 获取用户加入的所有家庭
   - 参数: 无
   - 返回: 家庭列表

## 3. 菜谱管理接口

1. **创建菜谱**
   - 接口: `/api/v1/recipes`
   - 方法: POST
   - 功能: 创建新菜谱
   - 参数: `title`, `description`, `ingredients`, `steps` 等
   - 返回: 创建的菜谱信息

2. **获取菜谱详情**
   - 接口: `/api/v1/recipes/{recipe_id}`
   - 方法: GET
   - 功能: 获取菜谱详细信息
   - 参数: 无
   - 返回: 菜谱详细信息

3. **更新菜谱**
   - 接口: `/api/v1/recipes/{recipe_id}`
   - 方法: PUT
   - 功能: 更新菜谱信息
   - 参数: `title`, `description`, `ingredients`, `steps` 等
   - 返回: 更新后的菜谱信息

4. **删除菜谱**
   - 接口: `/api/v1/recipes/{recipe_id}`
   - 方法: DELETE
   - 功能: 删除菜谱
   - 参数: 无
   - 返回: 操作结果

5. **获取我的菜谱列表**
   - 接口: `/api/v1/recipes/mine`
   - 方法: GET
   - 功能: 获取用户创建的菜谱列表
   - 参数: `page`, `limit`, `sort_by`, `filter`
   - 返回: 菜谱列表及分页信息

6. **获取收藏菜谱列表**
   - 接口: `/api/v1/recipes/favorites`
   - 方法: GET
   - 功能: 获取用户收藏的菜谱列表
   - 参数: `page`, `limit`, `sort_by`, `filter`
   - 返回: 菜谱列表及分页信息

7. **收藏菜谱**
   - 接口: `/api/v1/recipes/{recipe_id}/favorite`
   - 方法: POST
   - 功能: 收藏菜谱
   - 参数: 无
   - 返回: 操作结果

8. **取消收藏菜谱**
   - 接口: `/api/v1/recipes/{recipe_id}/favorite`
   - 方法: DELETE
   - 功能: 取消收藏菜谱
   - 参数: 无
   - 返回: 操作结果

9. **评价菜谱**
   - 接口: `/api/v1/recipes/{recipe_id}/reviews`
   - 方法: POST
   - 功能: 对菜谱进行评分和评论
   - 参数: `rating`, `content`, `images`
   - 返回: 创建的评论信息

10. **获取菜谱评论**
    - 接口: `/api/v1/recipes/{recipe_id}/reviews`
    - 方法: GET
    - 功能: 获取菜谱评论列表
    - 参数: `page`, `limit`
    - 返回: 评论列表及分页信息

11. **社区菜谱搜索**
    - 接口: `/api/v1/recipes/search`
    - 方法: GET
    - 功能: 搜索社区菜谱
    - 参数: `keyword`, `tags`, `cuisine_type`, `difficulty`, `cooking_time`, `page`, `limit`
    - 返回: 菜谱列表及分页信息

12. **菜谱推荐**
    - 接口: `/api/v1/recipes/recommendations`
    - 方法: GET
    - 功能: 获取个性化推荐菜谱
    - 参数: `type` (热门/新增/季节性)
    - 返回: 推荐菜谱列表

## 4. 点菜系统接口 (餐厅风格)

1. **创建菜单计划**
   - 接口: `/api/v1/menu-plans`
   - 方法: POST
   - 功能: 创建新的菜单计划
   - 参数: `name`, `date`, `meal_type`, `servings` 等
   - 返回: 创建的菜单计划信息

2. **获取菜单计划**
   - 接口: `/api/v1/menu-plans/{plan_id}`
   - 方法: GET
   - 功能: 获取菜单计划详情
   - 参数: 无
   - 返回: 菜单计划详情

3. **更新菜单计划基本信息**
   - 接口: `/api/v1/menu-plans/{plan_id}`
   - 方法: PUT
   - 功能: 更新菜单计划基本信息
   - 参数: `name`, `date`, `meal_type`, `servings` 等
   - 返回: 更新后的菜单计划信息

4. **添加菜品到菜单**
   - 接口: `/api/v1/menu-plans/{plan_id}/dishes`
   - 方法: POST
   - 功能: 向菜单添加菜品
   - 参数: `recipe_id`, `quantity`, `notes` 等
   - 返回: 添加的菜品信息

5. **从菜单移除菜品**
   - 接口: `/api/v1/menu-plans/{plan_id}/dishes/{dish_id}`
   - 方法: DELETE
   - 功能: 从菜单移除菜品
   - 参数: 无
   - 返回: 操作结果

6. **更新菜单中的菜品**
   - 接口: `/api/v1/menu-plans/{plan_id}/dishes/{dish_id}`
   - 方法: PUT
   - 功能: 更新菜单中的菜品信息
   - 参数: `quantity`, `notes` 等
   - 返回: 更新后的菜品信息

7. **获取菜品分类列表**
   - 接口: `/api/v1/dish-categories`
   - 方法: GET
   - 功能: 获取所有菜品分类
   - 参数: 无
   - 返回: 分类列表

8. **根据分类获取菜品**
   - 接口: `/api/v1/recipes/by-category/{category_id}`
   - 方法: GET
   - 功能: 获取特定分类下的菜品
   - 参数: `page`, `limit`
   - 返回: 菜品列表及分页信息

9. **添加菜单协作者**
   - 接口: `/api/v1/menu-plans/{plan_id}/collaborators`
   - 方法: POST
   - 功能: 添加菜单协作者
   - 参数: `user_id`, `role`
   - 返回: 更新后的协作者列表

10. **移除菜单协作者**
    - 接口: `/api/v1/menu-plans/{plan_id}/collaborators/{user_id}`
    - 方法: DELETE
    - 功能: 移除菜单协作者
    - 参数: 无
    - 返回: 操作结果

11. **获取用户的菜单计划**
    - 接口: `/api/v1/menu-plans/mine`
    - 方法: GET
    - 功能: 获取用户创建的菜单计划
    - 参数: `page`, `limit`, `status`
    - 返回: 菜单计划列表及分页信息

12. **获取家庭的菜单计划**
    - 接口: `/api/v1/menu-plans/by-family/{family_id}`
    - 方法: GET
    - 功能: 获取指定家庭的菜单计划
    - 参数: `page`, `limit`, `status`
    - 返回: 菜单计划列表及分页信息

## 5. 购物清单接口

1. **从菜单生成购物清单**
   - 接口: `/api/v1/shopping-lists/generate`
   - 方法: POST
   - 功能: 基于选定菜单生成购物清单
   - 参数: `plan_ids`, `name`
   - 返回: 生成的购物清单信息

2. **获取购物清单**
   - 接口: `/api/v1/shopping-lists/{list_id}`
   - 方法: GET
   - 功能: 获取购物清单详情
   - 参数: 无
   - 返回: 购物清单详情

3. **更新购物清单基本信息**
   - 接口: `/api/v1/shopping-lists/{list_id}`
   - 方法: PUT
   - 功能: 更新购物清单基本信息
   - 参数: `name`, `notes` 等
   - 返回: 更新后的购物清单信息

4. **添加购物项目**
   - 接口: `/api/v1/shopping-lists/{list_id}/items`
   - 方法: POST
   - 功能: 添加新的购物项目
   - 参数: `name`, `category`, `amount`, `unit`, `notes`
   - 返回: 添加的购物项目信息

5. **更新购物项目**
   - 接口: `/api/v1/shopping-lists/{list_id}/items/{item_id}`
   - 方法: PUT
   - 功能: 更新购物项目信息
   - 参数: `checked`, `amount`, `notes` 等
   - 返回: 更新后的购物项目信息

6. **删除购物项目**
   - 接口: `/api/v1/shopping-lists/{list_id}/items/{item_id}`
   - 方法: DELETE
   - 功能: 删除购物项目
   - 参数: 无
   - 返回: 操作结果

7. **购物清单协作**
   - 接口: `/api/v1/shopping-lists/{list_id}/share`
   - 方法: POST
   - 功能: 分享购物清单给其他用户
   - 参数: `user_ids`, `permissions`
   - 返回: 更新后的协作者列表

8. **导出购物清单**
   - 接口: `/api/v1/shopping-lists/{list_id}/export`
   - 方法: GET
   - 功能: 导出购物清单为文本或图片
   - 参数: `format` (text/image)
   - 返回: 导出的内容或下载URL

9. **获取用户的购物清单**
   - 接口: `/api/v1/shopping-lists/mine`
   - 方法: GET
   - 功能: 获取用户创建的购物清单
   - 参数: `page`, `limit`, `status`
   - 返回: 购物清单列表及分页信息

10. **批量更新购物项目状态**
    - 接口: `/api/v1/shopping-lists/{list_id}/items/batch-update`
    - 方法: PUT
    - 功能: 批量更新多个购物项目的状态
    - 参数: `item_ids`, `checked`
    - 返回: 更新结果

## 6. 智能食材合并接口

1. **食材智能识别**
   - 接口: `/api/v1/ingredients/recognize`
   - 方法: POST
   - 功能: 智能识别食材名称、分类和单位
   - 参数: `ingredient_text`
   - 返回: 识别结果

2. **食材信息获取**
   - 接口: `/api/v1/ingredients/{ingredient_id}`
   - 方法: GET
   - 功能: 获取食材详细信息
   - 参数: 无
   - 返回: 食材详细信息

3. **食材单位换算**
   - 接口: `/api/v1/ingredients/convert-unit`
   - 方法: POST
   - 功能: 进行食材单位换算
   - 参数: `ingredient_id`, `amount`, `from_unit`, `to_unit`
   - 返回: 换算结果

4. **搜索食材**
   - 接口: `/api/v1/ingredients/search`
   - 方法: GET
   - 功能: 搜索食材库
   - 参数: `keyword`, `category`
   - 返回: 食材列表

5. **食材合并预览**
   - 接口: `/api/v1/ingredients/merge-preview`
   - 方法: POST
   - 功能: 预览多个食材合并结果
   - 参数: `ingredients` (食材列表)
   - 返回: 合并后的食材列表

6. **获取食材分类**
   - 接口: `/api/v1/ingredients/categories`
   - 方法: GET
   - 功能: 获取食材分类列表
   - 参数: 无
   - 返回: 分类列表

7. **获取食材替代建议**
   - 接口: `/api/v1/ingredients/{ingredient_id}/substitutes`
   - 方法: GET
   - 功能: 获取食材的替代品建议
   - 参数: 无
   - 返回: 替代食材列表

## 7. 其他辅助接口

1. **文件上传**
   - 接口: `/api/v1/upload`
   - 方法: POST
   - 功能: 上传图片或其他文件
   - 参数: `file`, `type` (recipe/avatar/step)
   - 返回: 上传后的文件URL

2. **系统标签获取**
   - 接口: `/api/v1/tags`
   - 方法: GET
   - 功能: 获取系统标签列表
   - 参数: `type` (cuisine/category/season等)
   - 返回: 标签列表

3. **获取季节性推荐**
   - 接口: `/api/v1/seasonal-recommendations`
   - 方法: GET
   - 功能: 获取当前季节的食材和菜谱推荐
   - 参数: `season` (可选，默认为当前季节)
   - 返回: 季节性推荐信息

4. **家宴统计分析**
   - 接口: `/api/v1/analytics/meals`
   - 方法: GET
   - 功能: 获取用餐统计和分析
   - 参数: `time_range`, `family_id`
   - 返回: 统计分析数据

5. **用户反馈提交**
   - 接口: `/api/v1/feedback`
   - 方法: POST
   - 功能: 提交用户反馈或问题
   - 参数: `content`, `contact_info`, `type`
   - 返回: 提交结果

6. **系统配置获取**
   - 接口: `/api/v1/config`
   - 方法: GET
   - 功能: 获取系统配置信息
   - 参数: `type` (可选)
   - 返回: 系统配置

7. **小程序码生成**
   - 接口: `/api/v1/wxacode/generate`
   - 方法: POST
   - 功能: 生成小程序码
   - 参数: `page`, `scene`
   - 返回: 小程序码图片URL

8. **内容分享**
   - 接口: `/api/v1/share`
   - 方法: POST
   - 功能: 生成分享卡片和链接
   - 参数: `type`, `id`, `custom_message`
   - 返回: 分享信息

## 8. 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/登录过期 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 500 | 服务器内部错误 |

## 9. 接口通用规范

1. **请求格式**：
   - Content-Type: application/json
   - 请求体使用JSON格式

2. **响应格式**：
   ```json
   {
     "code": 200,
     "msg": "success",
     "data": {
       // 具体数据
     }
   }
   ```

3. **分页规范**：
   - 请求参数: `page`(页码，从1开始), `limit`(每页数量)
   - 响应数据:
   ```json
   {
     "list": [],
     "pagination": {
       "total": 100,
       "page": 1,
       "limit": 10,
       "pages": 10
     }
   }
   ```

4. **身份验证**：
   - 请求头携带Token: `Authorization: Bearer {token}`

5. **版本控制**：
   - 接口URL中包含版本号，如`/api/v1/`

## 10. 接口开发进度

| 接口模块 | 开发阶段 | 负责人 | 计划完成时间 |
|---------|---------|-------|------------|
| 用户认证 | 待开发   | -     | -          |
| 菜谱管理 | 待开发   | -     | -          |
| 点菜系统 | 待开发   | -     | -          |
| 购物清单 | 待开发   | -     | -          |
| 食材合并 | 待开发   | -     | -          |
| 辅助接口 | 待开发   | -     | -          | 
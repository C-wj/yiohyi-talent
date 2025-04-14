# 家宴菜谱小程序应用配置设计

本文档详细说明如何基于现有的微信小程序模板，修改`app.json`配置文件，以适应家宴菜谱小程序的需求。

## 1. 现有配置分析

当前项目的`app.json`配置如下：

```json
{
  "pages": ["pages/home/index", "pages/message/index", "pages/my/index"],
  "usingComponents": {
    "t-toast": "tdesign-miniprogram/toast/toast"
  },
  "subpackages": [
    {
      "root": "pages/search",
      "name": "search",
      "pages": ["index"]
    },
    {
      "root": "pages/my/info-edit",
      "name": "edit",
      "pages": ["index"]
    },
    {
      "root": "pages/chat",
      "name": "chat",
      "pages": ["index"]
    },
    {
      "root": "pages/login",
      "name": "login",
      "pages": ["login"]
    },
    {
      "root": "pages/loginCode",
      "name": "loginCode",
      "pages": ["loginCode"]
    },
    {
      "root": "pages/dataCenter",
      "name": "dataCenter",
      "pages": ["index"]
    },
    {
      "root": "pages/setting",
      "name": "setting",
      "pages": ["index"]
    },
    {
      "root": "pages/release",
      "name": "release",
      "pages": ["index"]
    }
  ],
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#fff",
    "navigationBarTitleText": "Weixin",
    "navigationBarTextStyle": "black"
  },
  "tabBar": {
    "custom": true,
    "list": [
      {
        "pagePath": "pages/home/index",
        "text": "首页"
      },
      {
        "pagePath": "pages/message/index",
        "text": "消息"
      },
      {
        "pagePath": "pages/my/index",
        "text": "我的"
      }
    ]
  },
  "resolveAlias": {
    "~/*": "/*"
  },
  "sitemapLocation": "sitemap.json"
}
```

## 2. 菜谱小程序配置修改方案

### 2.1 基本配置修改

```json
{
  "pages": [
    "pages/home/index",         // 社区菜谱首页
    "pages/my-recipes/index",   // 我的菜谱页
    "pages/order/index",        // 点菜系统页
    "pages/my/index"            // 个人中心页
  ],
  "usingComponents": {
    "t-toast": "tdesign-miniprogram/toast/toast",
    "t-tabs": "tdesign-miniprogram/tabs/tabs",
    "t-tab-panel": "tdesign-miniprogram/tabs/tab-panel",
    "t-image": "tdesign-miniprogram/image/image",
    "t-input": "tdesign-miniprogram/input/input",
    "t-checkbox": "tdesign-miniprogram/checkbox/checkbox",
    "t-checkbox-group": "tdesign-miniprogram/checkbox-group/checkbox-group",
    "t-rate": "tdesign-miniprogram/rate/rate",
    "t-stepper": "tdesign-miniprogram/stepper/stepper"
  },
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#FF9500",
    "navigationBarTitleText": "家宴菜谱",
    "navigationBarTextStyle": "white"
  },
  "tabBar": {
    "custom": true,
    "color": "#999999",
    "selectedColor": "#FF9500",
    "backgroundColor": "#ffffff",
    "borderStyle": "white",
    "list": [
      {
        "pagePath": "pages/home/index",
        "text": "社区"
      },
      {
        "pagePath": "pages/my-recipes/index",
        "text": "我的菜谱"
      },
      {
        "pagePath": "pages/order/index",
        "text": "点菜"
      },
      {
        "pagePath": "pages/my/index",
        "text": "我的"
      }
    ]
  }
}
```

### 2.2 子包配置修改

```json
"subpackages": [
  {
    "root": "pages/search",
    "name": "search",
    "pages": ["index"]
  },
  {
    "root": "pages/recipe",
    "name": "recipe",
    "pages": [
      "detail/index",      // 菜谱详情页
      "edit/index",        // 菜谱编辑页
      "create/index"       // 菜谱创建页
    ]
  },
  {
    "root": "pages/order",
    "name": "order",
    "pages": [
      "detail/index",       // 点菜详情页
      "calendar/index",     // 点菜日历页
      "add-dish/index"      // 添加菜品页
    ]
  },
  {
    "root": "pages/shopping",
    "name": "shopping",
    "pages": [
      "list/index",         // 购物清单页
      "history/index"       // 历史清单页
    ]
  },
  {
    "root": "pages/family",
    "name": "family",
    "pages": [
      "index",              // 家庭管理页
      "create/index",       // 创建家庭页
      "members/index"       // 成员管理页
    ]
  },
  {
    "root": "pages/login",
    "name": "login",
    "pages": ["login"]
  },
  {
    "root": "pages/setting",
    "name": "setting",
    "pages": ["index"]
  }
]
```

### 2.3 分包预下载配置

为提高用户体验，添加分包预下载配置：

```json
"preloadRule": {
  "pages/home/index": {
    "network": "all",
    "packages": ["search", "recipe"]
  },
  "pages/my-recipes/index": {
    "network": "all",
    "packages": ["recipe"]
  },
  "pages/order/index": {
    "network": "all",
    "packages": ["order", "shopping"]
  }
}
```

### 2.4 自定义组件配置

```json
"usingComponents": {
  "t-toast": "tdesign-miniprogram/toast/toast",
  "t-dialog": "tdesign-miniprogram/dialog/dialog",
  "t-tabs": "tdesign-miniprogram/tabs/tabs",
  "t-tab-panel": "tdesign-miniprogram/tabs/tab-panel",
  "t-loading": "tdesign-miniprogram/loading/loading",
  "t-image": "tdesign-miniprogram/image/image",
  "t-input": "tdesign-miniprogram/input/input",
  "t-textarea": "tdesign-miniprogram/textarea/textarea",
  "t-checkbox": "tdesign-miniprogram/checkbox/checkbox",
  "t-checkbox-group": "tdesign-miniprogram/checkbox-group/checkbox-group",
  "t-radio": "tdesign-miniprogram/radio/radio",
  "t-radio-group": "tdesign-miniprogram/radio-group/radio-group",
  "t-rate": "tdesign-miniprogram/rate/rate",
  "t-stepper": "tdesign-miniprogram/stepper/stepper",
  "t-swiper": "tdesign-miniprogram/swiper/swiper",
  "t-swiper-item": "tdesign-miniprogram/swiper/swiper-item",
  "t-dropdown-menu": "tdesign-miniprogram/dropdown-menu/dropdown-menu",
  "t-dropdown-item": "tdesign-miniprogram/dropdown-item/dropdown-item",
  "t-calendar": "tdesign-miniprogram/calendar/calendar",
  "t-tag": "tdesign-miniprogram/tag/tag",
  "t-uploader": "tdesign-miniprogram/upload/upload",
  "t-button": "tdesign-miniprogram/button/button",
  "t-grid": "tdesign-miniprogram/grid/grid",
  "t-grid-item": "tdesign-miniprogram/grid/grid-item",
  "t-empty": "tdesign-miniprogram/empty/empty",
  "t-switch": "tdesign-miniprogram/switch/switch",
  "t-cell": "tdesign-miniprogram/cell/cell",
  "t-cell-group": "tdesign-miniprogram/cell-group/cell-group",
  "t-count-down": "tdesign-miniprogram/count-down/count-down",
  "recipe-card": "/components/recipe-card/index",
  "ingredient-list": "/components/ingredient-list/index",
  "step-list": "/components/step-list/index",
  "dish-picker": "/components/dish-picker/index",
  "shopping-item": "/components/shopping-item/index"
}
```

## 3. 自定义TabBar配置

需要修改`/custom-tab-bar/index.js`文件，适配新的导航结构：

```javascript
const app = getApp();

Component({
  data: {
    value: '',
    list: [
      {
        icon: 'home',
        value: 'home',
        label: '社区',
      },
      {
        icon: 'app',
        value: 'my-recipes',
        label: '我的菜谱',
      },
      {
        icon: 'cart',
        value: 'order',
        label: '点菜',
      },
      {
        icon: 'user',
        value: 'my',
        label: '我的',
      },
    ],
  },
  lifetimes: {
    ready() {
      const pages = getCurrentPages();
      const curPage = pages[pages.length - 1];
      if (curPage) {
        const nameRe = /pages\/(\w+(-\w+)?)\/index/.exec(curPage.route);
        if (nameRe === null) return;
        if (nameRe[1] && nameRe) {
          this.setData({
            value: nameRe[1],
          });
        }
      }
    },
  },
  methods: {
    handleChange(e) {
      const { value } = e.detail;
      wx.switchTab({ url: `/pages/${value}/index` });
    },
  },
});
```

## 4. 图标资源配置

需要在`images`目录下准备以下图标资源：

- `home.png`：社区图标（未选中状态）
- `home-active.png`：社区图标（选中状态）
- `recipe.png`：我的菜谱图标（未选中状态）
- `recipe-active.png`：我的菜谱图标（选中状态）
- `order.png`：点菜图标（未选中状态）
- `order-active.png`：点菜图标（选中状态）
- `user.png`：我的图标（未选中状态）
- `user-active.png`：我的图标（选中状态）

图标规格：
- 尺寸：64x64像素（推荐）
- 格式：PNG格式，支持透明背景
- 未选中状态：灰色 #999999
- 选中状态：主题色 #FF9500

## 5. 主题配置

为实现统一的视觉风格，需要在`app.wxss`中定义主题色：

```css
/* app.wxss */
page {
  --primary-color: #FF9500;         /* 主题色：橙色 */
  --primary-color-light: #FFE4BF;   /* 主题色浅色 */
  --secondary-color: #4CAF50;       /* 辅助色：绿色 */
  --text-primary: #333333;          /* 主要文本色 */
  --text-secondary: #666666;        /* 次要文本色 */
  --text-placeholder: #999999;      /* 占位文本色 */
  --bg-primary: #FFFFFF;            /* 主背景色 */
  --bg-secondary: #F6F6F6;          /* 次背景色 */
  --border-color: #EEEEEE;          /* 边框色 */
  --error-color: #E53935;           /* 错误色 */
  --warning-color: #FFB300;         /* 警告色 */
  --success-color: #4CAF50;         /* 成功色 */

  background-color: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 28rpx;
  line-height: 1.5;
}
```

## 6. 页面配置详解

### 6.1 社区菜谱页 (pages/home/index.json)

```json
{
  "navigationBarTitleText": "社区菜谱",
  "enablePullDownRefresh": true,
  "usingComponents": {
    "t-swiper": "tdesign-miniprogram/swiper/swiper",
    "t-swiper-item": "tdesign-miniprogram/swiper-item/swiper-item",
    "t-search": "tdesign-miniprogram/search/search",
    "t-tabs": "tdesign-miniprogram/tabs/tabs",
    "t-tab-panel": "tdesign-miniprogram/tab-panel/tab-panel",
    "t-loading": "tdesign-miniprogram/loading/loading",
    "recipe-card": "/components/recipe-card/index"
  }
}
```

### 6.2 我的菜谱页 (pages/my-recipes/index.json)

```json
{
  "navigationBarTitleText": "我的菜谱",
  "enablePullDownRefresh": true,
  "usingComponents": {
    "t-search": "tdesign-miniprogram/search/search",
    "t-tabs": "tdesign-miniprogram/tabs/tabs",
    "t-tab-panel": "tdesign-miniprogram/tab-panel/tab-panel",
    "t-empty": "tdesign-miniprogram/empty/empty",
    "t-loading": "tdesign-miniprogram/loading/loading", 
    "t-button": "tdesign-miniprogram/button/button",
    "recipe-card": "/components/recipe-card/index"
  }
}
```

### 6.3 点菜系统页 (pages/order/index.json)

```json
{
  "navigationBarTitleText": "家庭点菜",
  "usingComponents": {
    "t-calendar": "tdesign-miniprogram/calendar/calendar",
    "t-tabs": "tdesign-miniprogram/tabs/tabs",
    "t-tab-panel": "tdesign-miniprogram/tab-panel/tab-panel",
    "t-empty": "tdesign-miniprogram/empty/empty",
    "t-button": "tdesign-miniprogram/button/button",
    "t-cell": "tdesign-miniprogram/cell/cell",
    "t-cell-group": "tdesign-miniprogram/cell-group/cell-group"
  }
}
```

## 7. 完整app.json配置

以下是家宴菜谱小程序完整的`app.json`配置：

```json
{
  "pages": [
    "pages/home/index",
    "pages/my-recipes/index",
    "pages/order/index",
    "pages/my/index"
  ],
  "subpackages": [
    {
      "root": "pages/search",
      "name": "search",
      "pages": ["index"]
    },
    {
      "root": "pages/recipe",
      "name": "recipe",
      "pages": [
        "detail/index",
        "edit/index",
        "create/index"
      ]
    },
    {
      "root": "pages/order",
      "name": "order",
      "pages": [
        "detail/index",
        "calendar/index",
        "add-dish/index"
      ]
    },
    {
      "root": "pages/shopping",
      "name": "shopping",
      "pages": [
        "list/index",
        "history/index"
      ]
    },
    {
      "root": "pages/family",
      "name": "family",
      "pages": [
        "index",
        "create/index",
        "members/index"
      ]
    },
    {
      "root": "pages/login",
      "name": "login",
      "pages": ["login"]
    },
    {
      "root": "pages/setting",
      "name": "setting",
      "pages": ["index"]
    }
  ],
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#FF9500",
    "navigationBarTitleText": "家宴菜谱",
    "navigationBarTextStyle": "white"
  },
  "tabBar": {
    "custom": true,
    "color": "#999999",
    "selectedColor": "#FF9500",
    "backgroundColor": "#ffffff",
    "borderStyle": "white",
    "list": [
      {
        "pagePath": "pages/home/index",
        "text": "社区"
      },
      {
        "pagePath": "pages/my-recipes/index",
        "text": "我的菜谱"
      },
      {
        "pagePath": "pages/order/index",
        "text": "点菜"
      },
      {
        "pagePath": "pages/my/index",
        "text": "我的"
      }
    ]
  },
  "usingComponents": {
    "t-toast": "tdesign-miniprogram/toast/toast",
    "t-dialog": "tdesign-miniprogram/dialog/dialog"
  },
  "preloadRule": {
    "pages/home/index": {
      "network": "all",
      "packages": ["search", "recipe"]
    },
    "pages/my-recipes/index": {
      "network": "all",
      "packages": ["recipe"]
    },
    "pages/order/index": {
      "network": "all",
      "packages": ["order", "shopping"]
    }
  },
  "resolveAlias": {
    "~/*": "/*"
  },
  "permission": {
    "scope.userLocation": {
      "desc": "你的位置信息将用于查找附近的食材价格信息"
    }
  },
  "sitemapLocation": "sitemap.json"
}
```

## 8. 配置实施步骤

1. **备份现有配置**：在修改前备份原有的`app.json`
2. **分步实施**：
   - 首先修改基本配置（pages、window、tabBar）
   - 然后添加分包配置
   - 最后添加组件和预加载规则
3. **配套修改**：
   - 更新`custom-tab-bar`组件
   - 设计并添加导航图标
   - 创建必要的页面文件结构
4. **测试验证**：
   - 确认导航可正常切换
   - 检查分包加载是否正常
   - 验证主题风格统一

通过以上配置修改，可以将现有的TDesign模板框架转换为适合家宴菜谱小程序的基础结构，为后续功能开发奠定基础。 
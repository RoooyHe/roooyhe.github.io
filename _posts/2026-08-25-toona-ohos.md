---
title: "toona ohos introduction"
date: 2026-08-25 00:50:00 +0800
last_modified_at: 2026-08-25 00:50:00 +0800
pin: false
---
一款面向 HarmonyOS 的原生 Matrix 客户端，采用深模块架构，严格依赖注入、平台抽象和显式接缝边界设计。参考 ElementX/Element Android 客户端架构。

## 功能特性

| 类别 | 功能 |
|------|------|
| **身份认证** | Homeserver 登录/注册，加密令牌持久化，自动会话恢复，令牌校验 |
| **同步** | 长轮询同步引擎，增量同步（since token），房间状态协调 |
| **房间** | 创建/加入/离开房间，房间别名，公共房间目录，房间设置 |
| **消息** | 文本/表情/通知消息，编辑/删除/回复，反应，贴纸，已读回执 |
| **空间** | 层级式房间组织，空间树导航，空间创建 |
| **端到端加密** | Olm/Megolm 加密，设备密钥管理，密钥验证（SAS + QR），设备信任级别 |
| **在线状态** | 用户在线状态，状态消息 |
| **媒体** | 图片上传/下载，缩略图生成，URL 预览 |
| **界面** | 深色/浅色主题，房间标签过滤（收藏、未读、私聊），通知角标 |

## 架构设计

```
toona/src/main/ets/
├── network/
│   ├── ConnectionConfig.ets       # 令牌 + 服务器接缝（拉取模型）
│   └── clients/
│       ├── BaseHttpClient.ets     # 通用 HTTP（request, requestBinary, requestMediaJson, upload）
│       ├── RoomHttpClient.ets     # 房间 + 输入状态 + 回执 API
│       ├── MessageHttpClient.ets  # 消息发送 + 关系 API
│       ├── UserHttpClient.ets     # 用户资料 API
│       ├── DeviceHttpClient.ets   # 设备密钥 API
│       ├── MediaHttpClient.ets    # 媒体上传/下载/缩略图
│       ├── PresenceHttpClient.ets # 在线状态 API
│       └── OpenIdHttpClient.ets   # OpenID 令牌 API
├── platform/
│   └── adapters/
│       ├── IFilePicker.ets        # 文件选择接口
│       ├── IAudioRecorder.ets     # 音频录制接口
│       ├── IClipboard.ets         # 剪贴板接口
│       ├── HarmonyFilePicker.ets  # PhotoPicker + 文件 I/O 实现
│       ├── HarmonyAudioRecorder.ets # 麦克风 + AV 录音实现
│       └── HarmonyClipboard.ets   # 剪贴板实现
├── models/
│   ├── DataModels.ets             # Session, Room, Message, User
│   └── types/                     # MatrixTypes, SyncTypes, RoomTypes, MessageTypes, CryptoTypes
├── database/
│   ├── LocalDatabase.ets          # SQLite 门面（Room ORM）
│   ├── ToonaDatabase.ets          # Room 数据库定义
│   ├── dao/                       # CryptoDao, DeviceKeysDao, MessageDao, RoomDao, UserDao
│   └── entities/                  # ORM 实体类
├── services/
│   ├── ServiceRegistry.ets        # AppStorage 支撑的服务定位器（init/getCurrent）
│   ├── AuthManager.ets            # IAuthManager 实现 — 登录、会话、令牌生命周期
│   ├── SyncManager.ets            # ISyncManager 实现 — 长轮询同步循环
│   ├── RoomManager.ets            # IRoomManager 实现 — 房间 CRUD
│   ├── MessageManager.ets         # 消息发送/编辑/删除
│   ├── CryptoService.ets          # 端到端加密：设备密钥、Megolm 会话、解密
│   ├── VerificationService.ets    # SAS + QR 密钥验证
│   ├── CryptoManager.ets          # 设备密钥上传、一次性密钥管理
│   ├── MediaManager.ets           # 媒体上传/下载/HTTP URL 生成
│   ├── DeviceManager.ets          # 设备列表管理
│   ├── FilterManager.ets          # 同步过滤器 CRUD
│   ├── PresenceManager.ets        # 在线状态管理
│   ├── PushManager.ets            # 推送规则管理
│   ├── RoomStateManager.ets       # 房间状态查询
│   ├── RoomTagManager.ets         # 房间标签（收藏）管理
│   ├── ThirdpartyManager.ets      # 第三方协议搜索
│   ├── UserManager.ets            # 用户资料管理
│   ├── VoIPManager.ets            # TURN 服务器凭证
│   ├── OpenIdManager.ets          # OpenID 令牌交换
│   ├── EventProcessor.ets         # Matrix 事件分发
│   ├── MessageActionHandler.ets   # 消息动作（发送/编辑/删除/置顶/反应/举报/分享/复制）
│   ├── MediaActionHandler.ets     # 媒体动作（选择图片/录音/上传）
│   └── RoomMetadataLoader.ets     # 房间主题 + 成员在线状态 + 输入状态
├── pages/
│   ├── AppNavigation.ets          # 根组合根（创建所有服务）
│   ├── LoginPage.ets              # 登录/注册
│   ├── MainPage.ets               # 带标签页的 Shell（房间/空间）
│   ├── RoomListPage.ets           # 带过滤的房间列表
│   ├── SpacePage.ets              # 空间树导航
│   ├── RoomDetailPage.ets         # 聊天视图（handlers + adapters 的组合根）
│   ├── SettingsPage.ets           # 用户设置 + 设备管理
│   └── ...                        # SearchPage, JoinRoomPage, JoinSpacePage 等
├── pages/components/
│   ├── MessageBubble.ets          # 消息显示（接收 mediaManager + verificationService）
│   ├── ImageViewer.ets            # 全屏图片（接收 mediaManager）
│   ├── FilePreview.ets            # 文件附件预览
│   └── verification/              # QrCodeVerificationDialog, SasVerificationDialog, VerificationRequestDialog
├── crypto/
│   ├── OlmWrapper.ets             # libolm 绑定
│   └── types/CryptoTypes.ets      # 加密类型定义
├── utils/
│   ├── AppLogger.ets              # 结构化日志
│   ├── ThemeManager.ets           # 主题 + 颜色系统
│   ├── MxcUtils.ets               # mxc:// URL 处理
│   ├── MessageFormatter.ets       # 纯格式化函数（时间、回复发送者）
│   ├── RoomStateParser.ets        # 房间状态事件 → Room 模型
│   └── ToastUtils.ets             # Toast 通知
└── toonaability/                  # ToonaAbility 入口
```

### 设计原则

**深模块，浅框架。** 每个服务拥有精简的公开接口（`IAuthManager`、`IRoomManager`、`ISyncManager`），将实现细节隐藏其后。横切关注点（文件选择、音频录制、剪贴板）通过平台适配器接口隔离。

**构造器注入，无隐藏单例。** 所有服务通过构造器参数接收依赖。组合根（`AppNavigation.initializeServices()`）负责装配整个依赖图。服务内部不调用 `getInstance()`——仅 Room ORM DAO 在初始化时使用。

**平台接缝。** `IFilePicker`、`IAudioRecorder`、`IClipboard` 将 HarmonyOS SDK API 隔离在接口之后。业务逻辑依赖接口，页面构造 Harmony 实现。

**服务注册表作为有界定位器。** NavDestination 页面（由 Navigation 框架实例化）通过 `ServiceRegistry.getCurrent()` 访问服务。这是定位器的唯一合法用途——内联子 `@Component` 页面通过父组件传递的属性接收依赖。

### 技术栈

| 层 | 技术 |
|---|------|
| 框架 | HarmonyOS + ArkTS 严格模式 |
| 架构 | MVVM + 仓库模式 + 构造器注入 |
| 导航 | NavPathStack / NavDestination（非 `@ohos.router`）|
| 存储 | SQLite（`@mlethe/room` ORM）+ `SPHelper` 加密偏好 |
| 网络 | `@kit.NetworkKit` HTTP 客户端（通过 `BaseHttpClient`）|
| 加密 | libolm（Olm + Megolm）（通过 `OlmWrapper`）|

### 依赖图

```
AppNavigation（组合根）
 ├── ConnectionConfig ←── AuthManager, 所有 HttpClients
 ├── AuthManager (IAuthManager) ←── SyncManager, RoomManager, MessageManager, ...
 ├── CryptoDao + DeviceKeysStorage ←── CryptoService, VerificationService
 ├── CryptoService ←── EventProcessor ←── SyncManager
 ├── 平台适配器 ←── MediaActionHandler, MessageActionHandler ←── RoomDetailPage
 └── ServiceRegistry（AppStorage 支撑）←── NavDestination 页面
```

## 快速开始

### 环境要求

- [DevEco Studio](https://developer.huawei.com/consumer/cn/deveco-studio/) 5.0+
- HarmonyOS SDK（API 12+）
- Node.js 18+（用于 hvigor 构建系统）

### 编译

```bash
# 调试编译
hvigor build -m toona

# 完整项目编译
hvigor build

# 清理编译产物
hvigor clean

# 发布编译
hvigor assembleRelease
```

### 运行

1. 在 DevEco Studio 中打开项目
2. 连接 HarmonyOS 设备或启动模拟器
3. 选择 `toona` 模块 → 运行

## 导航架构

应用使用 **NavPathStack / NavDestination**（非 `@ohos.router`）。

| 页面 | 类型 | 导航方式 |
|------|------|---------|
| `AppNavigation` | `@Entry` 根 | `Navigation(pathStack)` — 加载 LoginPage 或 MainPage |
| `LoginPage` | NavDestination | 首屏；登录后替换为 MainPage |
| `MainPage` | NavDestination | 带标签页 Shell（RoomListPage + SpacePage）|
| `RoomDetailPage` | NavDestination | 聊天视图，通过 `pushPathByName('RoomDetailPage', { roomId, roomName })` 推入 |
| `SettingsPage` | NavDestination | 设置页，通过 `pushPathByName('SettingsPage', ...)` 推入 |
| `RoomListPage` | `@Component` 子组件 | 由 MainPage 内嵌，通过 props 接收 `ISyncManager`、`IRoomManager`、`RoomTagManager` |
| `SpacePage` | `@Component` 子组件 | 由 MainPage 内嵌，通过 props 接收 `IRoomManager` |

子页面导航方式：

```typescript
this.pathStack.pushPathByName('RoomDetailPage', {
  "roomId": room.id,
  "roomName": room.getDisplayName()
} as Record<string, string>);
```

## 新增功能

### 1. 添加 API 端点

在对应的 `*HttpClient.ets` 中添加方法：

```typescript
// 在 RoomHttpClient.ets 中：
async getRoomTags(userId: string): Promise<RoomTagsResponse> {
  const encodedUserId = encodeURIComponent(userId);
  return await this.get<RoomTagsResponse>(`/user/${encodedUserId}/account_data/m.tag`);
}
```

如果 API 非常浅（仅 1 个方法，只是 `get`/`post` 的包装），添加到已有客户端——不要创建新客户端。

### 2. 添加响应类型

在 `models/types/MatrixTypes.ets` 中定义响应类型。

### 3. 添加服务方法

在对应的 Manager 中添加方法；如果是新领域，创建新 Manager。

### 4. 添加页面

1. 在 `pages/` 中创建 `.ets` 文件
2. 添加 `@Builder` 导出函数（`router_map.json` 要求）：

```typescript
@Builder
export function MyPageBuilder(name: string, param: Object) {
  MyPage()
}
```

3. 在 `resources/base/profile/router_map.json` 和 `main_pages.json` 中注册
4. 如果是内联子 `@Component`，通过 props 接收依赖（非 ServiceRegistry）

### 5. 在组合根中装配

新增服务：在 `AppNavigation.initializeServices()` 中创建实例，注册到 `ServiceRegistry`。

## 测试

- **单元测试**：`toona/src/test/**/*.test.ets` — 通过 DevEco Studio 测试运行器或 `hvigor test` 执行
- **设备测试**：`toona/src/ohosTest/ets/test/*.test.ets`
- **测试框架**：`@ohos/hypium`

## 代码规范

本项目强制执行 **ArkTS 严格模式**（`arkts-*` 规则标签）：

| 规则 | 说明 |
|------|------|
| `arkts-no-standalone-this` | 禁止在类方法外使用 `this` |
| `arkts-no-untyped-obj-literals` | 对象字面量必须有显式类型上下文 |
| `arkts-no-any-unknown` | 禁止 `any` 或 `unknown` 类型 |
| `arkts-no-destructuring` | 禁止解构声明 |
| `arkts-no-as-const` | 禁止 `as const` 断言 |

额外约定：
- 所有变量和参数必须有显式类型注解
- `throw new Error(...)` — 禁止抛出字符串
- 使用 `NavPathStack` / `NavDestination` — 禁止 `@ohos.router`
- 构造器注入 — 服务类内部禁止 `getInstance()`
- 使用 `@kit.NetworkKit` HTTP — 禁止 `fetch()`
一款面向 HarmonyOS 的原生 Matrix 客户端，采用深模块架构，严格依赖注入、平台抽象和显式接缝边界设计。参考 ElementX/Element Android 客户端架构。

## 功能特性

| 类别 | 功能 |
|------|------|
| **身份认证** | Homeserver 登录/注册，加密令牌持久化，自动会话恢复，令牌校验 |
| **同步** | 长轮询同步引擎，增量同步（since token），房间状态协调 |
| **房间** | 创建/加入/离开房间，房间别名，公共房间目录，房间设置 |
| **消息** | 文本/表情/通知消息，编辑/删除/回复，反应，贴纸，已读回执 |
| **空间** | 层级式房间组织，空间树导航，空间创建 |
| **端到端加密** | Olm/Megolm 加密，设备密钥管理，密钥验证（SAS + QR），设备信任级别 |
| **在线状态** | 用户在线状态，状态消息 |
| **媒体** | 图片上传/下载，缩略图生成，URL 预览 |
| **界面** | 深色/浅色主题，房间标签过滤（收藏、未读、私聊），通知角标 |

### 设计原则

**深模块，浅框架。** 每个服务拥有精简的公开接口（`IAuthManager`、`IRoomManager`、`ISyncManager`），将实现细节隐藏其后。横切关注点（文件选择、音频录制、剪贴板）通过平台适配器接口隔离。

**构造器注入，无隐藏单例。** 所有服务通过构造器参数接收依赖。组合根（`AppNavigation.initializeServices()`）负责装配整个依赖图。服务内部不调用 `getInstance()`——仅 Room ORM DAO 在初始化时使用。

**平台接缝。** `IFilePicker`、`IAudioRecorder`、`IClipboard` 将 HarmonyOS SDK API 隔离在接口之后。业务逻辑依赖接口，页面构造 Harmony 实现。

**服务注册表作为有界定位器。** NavDestination 页面（由 Navigation 框架实例化）通过 `ServiceRegistry.getCurrent()` 访问服务。这是定位器的唯一合法用途——内联子 `@Component` 页面通过父组件传递的属性接收依赖。

### 技术栈

| 层 | 技术 |
|---|------|
| 框架 | HarmonyOS + ArkTS 严格模式 |
| 架构 | MVVM + 仓库模式 + 构造器注入 |
| 导航 | NavPathStack / NavDestination（非 `@ohos.router`）|
| 存储 | SQLite（`@mlethe/room` ORM）+ `SPHelper` 加密偏好 |
| 网络 | `@kit.NetworkKit` HTTP 客户端（通过 `BaseHttpClient`）|
| 加密 | libolm（Olm + Megolm）（通过 `OlmWrapper`）|

### 依赖图

```
AppNavigation（组合根）
 ├── ConnectionConfig ←── AuthManager, 所有 HttpClients
 ├── AuthManager (IAuthManager) ←── SyncManager, RoomManager, MessageManager, ...
 ├── CryptoDao + DeviceKeysStorage ←── CryptoService, VerificationService
 ├── CryptoService ←── EventProcessor ←── SyncManager
 ├── 平台适配器 ←── MediaActionHandler, MessageActionHandler ←── RoomDetailPage
 └── ServiceRegistry（AppStorage 支撑）←── NavDestination 页面
```

## 快速开始

### 环境要求

- [DevEco Studio](https://developer.huawei.com/consumer/cn/deveco-studio/) 5.0+
- HarmonyOS SDK（API 12+）
- Node.js 18+（用于 hvigor 构建系统）

### 编译

```bash
# 调试编译
hvigor build -m toona

# 完整项目编译
hvigor build

# 清理编译产物
hvigor clean

# 发布编译
hvigor assembleRelease
```

### 运行

1. 在 DevEco Studio 中打开项目
2. 连接 HarmonyOS 设备或启动模拟器
3. 选择 `toona` 模块 → 运行

## 导航架构

应用使用 **NavPathStack / NavDestination**（非 `@ohos.router`）。

| 页面 | 类型 | 导航方式 |
|------|------|---------|
| `AppNavigation` | `@Entry` 根 | `Navigation(pathStack)` — 加载 LoginPage 或 MainPage |
| `LoginPage` | NavDestination | 首屏；登录后替换为 MainPage |
| `MainPage` | NavDestination | 带标签页 Shell（RoomListPage + SpacePage）|
| `RoomDetailPage` | NavDestination | 聊天视图，通过 `pushPathByName('RoomDetailPage', { roomId, roomName })` 推入 |
| `SettingsPage` | NavDestination | 设置页，通过 `pushPathByName('SettingsPage', ...)` 推入 |
| `RoomListPage` | `@Component` 子组件 | 由 MainPage 内嵌，通过 props 接收 `ISyncManager`、`IRoomManager`、`RoomTagManager` |
| `SpacePage` | `@Component` 子组件 | 由 MainPage 内嵌，通过 props 接收 `IRoomManager` |

子页面导航方式：

```typescript
this.pathStack.pushPathByName('RoomDetailPage', {
  "roomId": room.id,
  "roomName": room.getDisplayName()
} as Record<string, string>);
```

## 新增功能

### 1. 添加 API 端点

在对应的 `*HttpClient.ets` 中添加方法：

```typescript
// 在 RoomHttpClient.ets 中：
async getRoomTags(userId: string): Promise<RoomTagsResponse> {
  const encodedUserId = encodeURIComponent(userId);
  return await this.get<RoomTagsResponse>(`/user/${encodedUserId}/account_data/m.tag`);
}
```

如果 API 非常浅（仅 1 个方法，只是 `get`/`post` 的包装），添加到已有客户端——不要创建新客户端。

### 2. 添加响应类型

在 `models/types/MatrixTypes.ets` 中定义响应类型。

### 3. 添加服务方法

在对应的 Manager 中添加方法；如果是新领域，创建新 Manager。

### 4. 添加页面

1. 在 `pages/` 中创建 `.ets` 文件
2. 添加 `@Builder` 导出函数（`router_map.json` 要求）：

```typescript
@Builder
export function MyPageBuilder(name: string, param: Object) {
  MyPage()
}
```

3. 在 `resources/base/profile/router_map.json` 和 `main_pages.json` 中注册
4. 如果是内联子 `@Component`，通过 props 接收依赖（非 ServiceRegistry）

### 5. 在组合根中装配

新增服务：在 `AppNavigation.initializeServices()` 中创建实例，注册到 `ServiceRegistry`。

## 测试

- **单元测试**：`toona/src/test/**/*.test.ets` — 通过 DevEco Studio 测试运行器或 `hvigor test` 执行
- **设备测试**：`toona/src/ohosTest/ets/test/*.test.ets`
- **测试框架**：`@ohos/hypium`

## 代码规范

本项目强制执行 **ArkTS 严格模式**（`arkts-*` 规则标签）：

| 规则 | 说明 |
|------|------|
| `arkts-no-standalone-this` | 禁止在类方法外使用 `this` |
| `arkts-no-untyped-obj-literals` | 对象字面量必须有显式类型上下文 |
| `arkts-no-any-unknown` | 禁止 `any` 或 `unknown` 类型 |
| `arkts-no-destructuring` | 禁止解构声明 |
| `arkts-no-as-const` | 禁止 `as const` 断言 |

额外约定：
- 所有变量和参数必须有显式类型注解
- `throw new Error(...)` — 禁止抛出字符串
- 使用 `NavPathStack` / `NavDestination` — 禁止 `@ohos.router`
- 构造器注入 — 服务类内部禁止 `getInstance()`
- 使用 `@kit.NetworkKit` HTTP — 禁止 `fetch()`

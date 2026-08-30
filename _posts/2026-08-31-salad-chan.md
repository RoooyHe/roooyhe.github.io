---
title: "Salad-chan introduction"
date: 2026-08-31 00:00:08 +0800
last_modified_at: 2026-08-31 00:00:08 +0800
pin: false
---

# Salad-chan 🥗🐾

Salad-chan 是一款主打隐私的情侣共同减脂 App：两位伴侣各自记录每日热量摄入，一只共享的虚拟宠物把两人的健康史具象化——只要一起待在健康区间里，就能把它喂得白白胖胖。

所有数据只保存在本地（SQLite），唯一的网络行为是在局域网内两台设备之间直连交换日汇总，**绝不上传互联网**。

基于 [Expo SDK 57](https://docs.expo.dev/versions/v57.0.0/)、[expo-router](https://docs.expo.dev/router/introduction/) 与 React 19 构建。

## 功能特性

- **智能生成减脂目标** —— 填写身体素质（性别、年龄、身高、体重、活动量）后，本地用 Mifflin-St Jeor 公式算出每日热量目标，得到一个健康区间 `[下限, 目标]`。
- **每日热量记录** —— 手动输入今日摄入，或从内置食物库（50+ 种常见食物及热量估算）一键点选。
- **每日健康判定** —— 按自然日对每日摄入判定：
  - 落在 `[下限, 目标]` 内 → **健康**
  - 超过目标 → **暴食**
  - 低于下限 → **营养不良**
  - 采用懒结算：次日首次打开 App 时才结算前一天。
- **共享虚拟宠物** 🐾 —— 一只幻想系小生物，是两人健康史的具象化。当日状态由两人中较差一方决定：
  - 两人都健康 → 吃饱
  - 一方暴食 → 挨饿
  - 一方营养不良 → 营养不良
- **成长值与连胜** —— 每个结算日累计成长值：双方都健康按连胜加成（连续健康天数越多，单日收益越高，+3 → +4 → …）；恰好一人健康 +0；双方都不健康 −2。宠物不会死亡，最坏只是持续呈现营养不良的外观。
- **4 个成长阶段** —— 幼年 → 成长 → 成年 → 完全体（成长值阈值：0 / 30 / 90 / 200）。
- **局域网情侣配对** —— 一台设备创建房间并显示 6 位配对码，另一半在同一 Wi-Fi 下输入即可绑定。mDNS 发现 + TCP 直连；配对后双方只认持久化的设备标识。
- **只同步日汇总** —— 同步只交换每天的摄入总量与判定结果，绝不交换饮食明细；合并逻辑确定性收敛，双方重放输入一致。
- **改历史整体重算** —— 修改或删除任意一天，宠物状态都会从记录全量重放得出。
- **本地每日提醒** —— 可选本地通知（默认 20:00，可改可关），提醒记录，不联网。
- **深色模式** —— 自动跟随系统明暗主题。

## 隐私与设计原则

- **本地优先**：所有数据都存在本地 SQLite（`salad-chan.db`），没有后端、没有账号体系、没有云组件。
- **仅局域网共享**：唯一的网络行为是在局域网内直接交换日汇总，见 [ADR 0001](docs/adr/0001-no-backend-formula-based-goals.md)。
- **确定性重放**：`src/core/settlement.ts` 是唯一权威——宠物的一切状态（当日状态、成长值、连胜、阶段）都由两人每日记录序列重放确定性推出；本地显示、改历史、局域网补传共用同一个函数收敛。

## 技术栈

| 层 | 选型 |
| --- | --- |
| 框架 | Expo SDK 57（`expo@~57.0.15`） |
| 路由 | expo-router（文件式路由，原生标签页） |
| UI | React Native 0.86、react-native-reanimated 4、expo-image、expo-glass-effect |
| 存储 | expo-sqlite（WAL 模式） |
| 通知 | expo-notifications（单条本地每日提醒） |
| 局域网同步 | react-native-zeroconf（mDNS/Bonjour）+ react-native-tcp-socket |
| 语言 | TypeScript ~6.0（strict） |
| 测试 | jest-expo |

> **注意**：`react-native-zeroconf` 与 `react-native-tcp-socket` 均为原生模块，局域网配对需要 development build，**在 Expo Go 中不可用**。

## 快速开始

### 环境要求

- Node.js 与 npm
- [Expo CLI](https://docs.expo.dev/more/create-expo/)（或直接用 `npx`）
- 端到端验证局域网同步需要：development build + 两台同一 Wi-Fi 下的真机

### 安装与运行

```bash
npm install
npx expo start
```

从终端输出中选择在 Android 模拟器、iOS 模拟器、浏览器或真机上打开。

其它脚本：

```bash
npm run android   # expo run:android
npm run ios       # expo run:ios
npm run web       # expo start --web
npm run lint      # expo lint
npm test          # jest（核心领域逻辑）
```

## 项目结构

```
src/
├── core/                  # 纯领域逻辑——无 UI、无 RN 依赖（可单测）
│   ├── judgment.ts        # 健康判定：[下限, 目标] → 健康/暴食/营养不良
│   ├── settlement.ts      # 懒结算 + 全量重放：f(两人每日记录) → 成长/连胜/阶段/当日状态
│   ├── goal.ts            # Mifflin-St Jeor 公式 → 目标/下限
│   ├── sync.ts            # 确定性的同步载荷构造与合并
│   ├── reminder.ts        # 每日提醒触发器构造
│   └── foods.ts           # 内置食物库（名称 → 热量估算）
├── db/                    # expo-sqlite 封装：日记录、目标、配对、对方日汇总、设备标识
├── sync/                  # mDNS 发现、配对握手、日汇总交换
│   ├── lan.ts             # 传输层：mDNS 发布/扫描 + TCP 直连
│   └── sync-now.ts        # 编排：汇总 → 交换 → 合并 → 落库
├── notifications/         # expo-notifications 薄壳（单条每日提醒）
├── hooks/                 # useSettlement（懒结算视图）、useTheme
├── components/            # 主题化 UI 组件、标签页、宠物动效图标
├── constants/             # 设计令牌 / 主题
└── app/                   # expo-router 页面（文件式路由）
```

## 页面

| 路由 | 页面 | 作用 |
| --- | --- | --- |
| `/` | 宠物首页 | 今日宠物状态、成长值、连胜、阶段 |
| `/onboarding` | 引导 | 身体素质 → 生成目标 → 领养宠物 |
| `/log` | 记录 | 记今日热量（手动 + 食物库） |
| `/history` | 历史 | 查看/修改/删除历史（触发重算） |
| `/partner` | 伴侣 | 创建/加入房间、配对/解绑、同步状态 |
| `/settings` | 设置 | 调整目标/下限、配置每日提醒 |

## 核心概念

完整词汇表见 [CONTEXT.md](CONTEXT.md)。关键术语：

- **目标 / 下限** —— 每日热量上限与下限，健康区间为 `[下限, 目标]`。
- **宠物当日状态** —— 宠物即时表现，由两人中较差一方的判定决定。
- **成长值** —— 决定成长阶段的累积分数（每日 +连胜加成 / 0 / −2）。
- **连胜** —— 两人连续健康的天数，天数越多单日成长收益越高。
- **配对** —— 一次性握手：一台设备创建房间生成 6 位配对码，另一方在同一局域网输入完成绑定。
- **解绑** —— 解除配对，成长值清零，新关系 = 新宠物。

## 测试

`src/core/` 中的纯领域逻辑用 jest-expo 做单元测试：

```bash
npm test
```

已覆盖模块：`judgment`、`settlement`、`goal`、`sync`、`foods`。

## 部署（EAS）

`eas.json` 定义了 `development`、`preview`、`production` 三个构建配置；`production` 使用远端版本源并自动递增。EAS 项目 ID 为 `cc4d8488-5c2b-41a1-95c9-44cece758d45`（owner `roooyhes-team`）。

```bash
eas build --profile development   # 开发客户端，用于真机局域网联调
eas build --profile preview
eas build --profile production
```

## 路线图 / v1 明确不做

详见 [v1-plan.md](docs/v1-plan.md)。v1 明确**不做**：

- 后端 / 账号 / 云同步
- 拍照识别、第三方食物 API
- 宠物死亡；真 AI 生成目标（v1 用公式兜底，AI 是 v2 候选）
- 共享宠物以外的社交、多伴侣

---

给一起努力变健康的情侣，做得更有爱一点 💙

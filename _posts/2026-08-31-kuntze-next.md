---
title: "kuntze next introduction"
date: 2026-08-31 00:24:00 +0800
last_modified_at: 2026-08-31 00:24:00 +0800
pin: false
---
# Kuntze — 茶叶价格追踪器

> 记录茶价，算清斤价 — 把每一次买入变成可比较的价格数据。

Kuntze 是一个单租户的内部茶叶价格追踪工具。录入一次买入记录 —— 总价、单份克重、份数 —— Kuntze 会自动换算克价、斤价（每 500 克）以及各泡法单价（5g / 6g / 7g / 8.3g），并把价格走势绘制成随时间更新的曲线。

技术栈：[Next.js](https://nextjs.org)（App Router）+ [Supabase](https://supabase.com)（认证 + Postgres）。

## 功能

- **快速录价**（`/`）— 搜索或选择系列/套装，输入总价，回车即可。规格自动带出，录入后价格走势图即时更新。可切换为仅展示追踪系列。
- **价格监控**（`/price`）— 某一 SKU 的全部价格记录，含走势图（总价与标价、斤价、常见规格价），支持完整的新增/查看/编辑/删除。
- **系列管理**（`/series`）— 品牌、产地、年份、规格（单份克重 × 份数）、标价、追踪标记与多选香型。选中香型后自动同步生成对应单品 SKU。
- **套装管理**（`/bundle`）— 套装本身是一个 SKU，由若干单品 SKU 组成；总克重从 `bundle_item` 即时聚合，不与单品口径混算。
- **SKU 管理**（`/sku`）— 统一查看所有单品与套装 SKU，含编码、品牌/系列/香型关联与标价。
- **茶叶分类**（`/tea-class`）— 三级分类树：品类 → 品种 → 香型。
- **品牌管理**（`/brand`）— 简单的新增/编辑/删除。
- **官网落地页**（`/marketing`）— 功能/口径/价格/FAQ 页面，也是唯一可被爬虫收录的公开路由。

## 价格口径

| 口径 | 来源 | 算法 |
| --- | --- | --- |
| 总价 | 录入 | 实际支付金额 |
| 总克重 | 自动 | 单品：`series.gram_per_piece × series.piece_count`；套装：`Σ (bundle_item.piece_count × gram_per_piece)` |
| 克价 | 自动 | `总价 ÷ 总克重` |
| 斤价 | 自动 | `克价 × 500` |
| 泡法单价 | 自动 | `克价 × 5g / 6g / 7g / 8.3g` |

## 技术栈

- **Next.js 16.3.1**（App Router）、**React 19**、**TypeScript 5**（严格模式）
- **Supabase** — `@supabase/ssr` + `@supabase/supabase-js`，负责认证、数据库与 SSR Cookie 处理
- **Tailwind CSS 4**，自定义设计令牌系统（`tokens.css`，珊瑚色/暖灰主题）
- **shadcn/ui** 组件（`@/components/ui`）+ **lucide-react** 图标
- **recharts** 价格走势图
- **class-variance-authority** + `clsx` + `tailwind-merge`

## 快速开始

### 环境要求

- Node.js 20+，以及你喜欢的包管理器（`bun` / `npm` / `pnpm` / `yarn`）
- 一个 Supabase 项目（用于认证与 Postgres 数据库）

### 环境变量

在项目根目录创建 `.env.local`：

```bash
NEXT_PUBLIC_SUPABASE_URL=你的项目地址
NEXT_PUBLIC_SUPABASE_ANON_KEY=你的匿名密钥
```

无需其他密钥 —— 所有数据库访问均通过受 RLS 策略约束的 Supabase 匿名密钥进行。

### 安装与运行

```bash
bun install        # 或 npm install / pnpm install
bun run dev        # 启动开发服务器（Next.js）
```

生产环境：

```bash
bun run build
bun run start
```

### 数据库初始化

迁移脚本位于 `supabase/migrations/`，按顺序执行：

1. `0001_series_spec_slim_price_monitor.sql` — 把克重/份数规格下沉到 `series`，`price_monitor` 瘦身为只存价格。
2. `0002_series_tracking.sql` — 为 `series` 增加 `is_tracked` 追踪标记。
3. `0003_sku_code_aroma.sql` — 为 `sku` 增加唯一编码 `code` 与关联 `tea_class` 的 `aroma_id`。

可通过 Supabase CLI（`supabase db push`）或 Supabase 的 SQL 编辑器执行。

## 数据库结构

```
brand ──< series ──< sku ──< price_monitor
                     │
                     ├──< bundle（与 sku 一对一，kind='bundle'）
                     │      └──< bundle_item >── tea_sku_id → sku
                     │
                     └── aroma_id → tea_class（品类 → 品种 → 香型）
```

| 表 | 说明 |
| --- | --- |
| `brand` | id, name, created_at |
| `series` | id, brand_id, name, year, origin, gram_per_piece, piece_count, list_price, is_tracked, created_at |
| `sku` | id, kind（`'tea'` / `'bundle'`）, name, code（唯一）, list_price, series_id, aroma_id, created_at |
| `bundle` | sku_id（与 `sku` 一对一） |
| `bundle_item` | bundle_sku_id, tea_sku_id, piece_count, gram_per_piece |
| `price_monitor` | id, sku_id, total_price, recorded_at |
| `tea_class` | id, name, level（`category` / `variety` / `aroma`）, parent_id（自引用树） |
| `series_aroma` | 关联表 `series_id` ↔ `aroma_id` |
| `tea_class_tree`（视图） | 品类/品种/香型扁平化行 |

类型化的 Supabase 客户端类型：`src/lib/supabase/database.types.ts`。

## 项目结构

```
src/
  app/            # App Router 页面与布局
    api/price/trend/   # 走势 API 路由（用派生价格丰富记录）
  components/     # 共享 React 组件（外壳、表单、图表、导航、ui/）
  lib/            # 工具、格式化、Supabase 客户端工厂
    supabase/     # server.ts、client.ts、middleware.ts、database.types.ts
  middleware.ts   # 会话刷新 + 登录重定向
supabase/
  migrations/     # SQL 迁移
public/           # 静态资源
```

## 路由

| 路由 | 访问权限 | 用途 |
| --- | --- | --- |
| `/` | 登录后 | 快速录价 + 实时走势图 |
| `/login`、`/register` | 公开 | Supabase 邮箱/密码认证 |
| `/marketing` | 公开 | 官网落地页（可被爬虫收录） |
| `/series` | 登录后 | 系列列表 / 新增 / 详情 / 编辑 |
| `/bundle` | 登录后 | 套装列表 / 新增 / 详情 / 编辑 |
| `/sku` | 登录后 | SKU 列表 |
| `/price` | 登录后 | 价格记录 + 走势图；新增 / 详情 / 编辑 |
| `/tea-class` | 登录后 | 三级分类树 |
| `/brand` | 登录后 | 品牌新增/编辑/删除 |
| `/api/price/trend` | 登录后 | 单个 SKU 的走势 JSON |

除 `/login`、`/register`、`/marketing` 和静态资源外，其余所有路由均由中间件（`src/middleware.ts`）保护：刷新 Supabase 会话 Cookie，并把未登录访客重定向到 `/login`。

## 开发约定

- **服务端组件** 直接用 `@/lib/supabase/server` 的 `createClient()` 拉取数据；不应被缓存的页面使用 `export const dynamic = "force-dynamic"`。
- **客户端组件** 以 `"use client"` 开头，并使用 `@/lib/supabase/client` 的浏览器客户端。
- 界面文案为简体中文；内联错误/加载状态如「加载失败 / 保存中… / 暂无数据」。
- 路径别名 `@/*` 映射到 `./src/*`。
- 不使用全局状态管理库 —— 状态为组件局部，或由服务端组件 props 下发。
- 目前尚未配置测试框架；如后续补充测试，建议与被测代码放在一起。

## 部署

部署到 **Vercel**，作为标准 Next.js 应用，配置上述两个环境变量即可。生产流程为 `next build` → `next start`。

## 许可证

私有项目 —— 目前未指定许可证。

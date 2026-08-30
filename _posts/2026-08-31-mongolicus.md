---
title: "mongolicus introduction"
date: 2026-08-31 01:18:08 +0800
last_modified_at: 2026-08-31 01:18:08 +0800
pin: false
---

# Mongolicus

基于 [MNN](https://github.com/alibaba/MNN) 推理引擎与 Qwen 模型构建的**端侧（On-device）LLM 聊天应用**。所有推理均在设备本地完成，无需云端 API。

使用 **Kotlin**、**Jetpack Compose** 与 **C++（JNI）** 开发。

## 功能特性

- 🧠 **完全本地推理** — 基于 MNN-LLM，使用 Qwen ChatML 对话格式
- ⚡ **流式生成** — 逐 token 实时输出，并带有动画指示器
- 💬 **多会话支持** — 自动以第一条用户消息命名会话
- 📱 **自适应布局** — 手机端单栏、平板/宽屏（≥ 600dp）侧边栏 + 聊天区双栏
- 🎛️ **可调节生成参数** — 温度、Top-P、重复惩罚、最大 token 数
- 🌗 **浅色 / 深色主题** — 基于 Material 3
- 📋 消息气泡支持文本复制（`SelectionContainer`）

## 架构

| 层 | 目录 | 说明 |
|-------|-----------|-------------|
| 引擎层 | `app/src/main/java/com/mongolicus/engine/` | Kotlin JNI 桥接层，对接 MNN 原生库 |
| 原生层 | `app/src/main/cpp/` | C++ MNN-LLM 推理引擎（JNI 实现） |
| 数据层 | `app/src/main/java/com/mongolicus/data/` | 数据模型与仓库层 |
| ViewModel | `app/src/main/java/com/mongolicus/viewmodel/` | 负责状态管理的 AndroidViewModel |
| UI 层 | `app/src/main/java/com/mongolicus/ui/` | Jetpack Compose UI 组件与界面 |

```
┌──────────────────────────────────────────────────────────┐
│                      UI（Compose）                        │
│   ChatScreen · ChatBubble · ChatInputBar · Sidebar       │
└───────────────────────────┬──────────────────────────────┘
                            │ StateFlow
┌───────────────────────────▼──────────────────────────────┐
│                  ChatViewModel（AndroidViewModel）        │
└───────────────────────────┬──────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────┐
│                 ChatRepository（会话管理）                 │
└───────────────────────────┬──────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────┐
│               QwenEngine（Kotlin JNI 桥接层）             │
└───────────────────────────┬──────────────────────────────┘
                            │ JNI
┌───────────────────────────▼──────────────────────────────┐
│          native-lib.cpp（C++ MNN::Transformer::Llm）      │
│                    MNN · Qwen MNN 模型                    │
└──────────────────────────────────────────────────────────┘
```

## 核心组件

### QwenEngine（JNI 桥接层）

- `QwenEngine.kt` — Kotlin 封装，通过 JNI 暴露 MNN 推理能力。提供 `init()`、`generate()`、`generateStream()`（阻塞式）、`generateSuspend()`（协程友好）、`encode()` / `decode()` 以及 `getModelInfo()`。原生库（`libmongolicus_mnn.so`）通过 `loadNativeLibrary()` 只加载一次。
- `native-lib.cpp` — C++ 实现，封装 `MNN::Transformer::Llm`：通过 `Llm::create()` + `load()` 初始化，通过 `response()` 接口进行流式生成（每个 token 通过 JNI 回调返回），并提供分词器 `encode()` / `decode()`。

### 聊天系统

- `ChatModels.kt` — 数据模型：`ChatMessage`、`MessageRole`、`Conversation`、`ModelConfig`、`GenerationParams` 以及 `PromptTemplate`（构造 Qwen ChatML 提示词）。
- `ChatRepository.kt` — 管理会话历史（新建 / 切换 / 删除），编排流式推理，自动为会话命名，并暴露生成参数。
- `ChatViewModel.kt` — `AndroidViewModel`，向 Compose UI 暴露 `ChatUiState` 与会话列表，负责引擎生命周期管理。

### UI（Compose）

- `ChatScreen.kt` — 主界面，自适应手机 / 平板布局，自动滚动到最新消息。
- `ChatBubble.kt` — 消息气泡，含角色标签、文本复制与流式动画指示器；同时包含 `EmptyChatPlaceholder` 空状态占位。
- `ChatInputBar.kt` — 输入框、发送按钮，以及可折叠的 `GenerationSettingsPanel` 参数面板（滑块调节）。
- `ConversationSidebar.kt` — 宽屏下的会话列表，支持新建 / 删除 / 设置操作。
- `Theme.kt` / `Color.kt` / `Type.kt` — Material 3 主题。

## 环境准备

### 前置要求

- Android Studio（建议 Hedgehog 或更高版本）
- JDK 17
- Android SDK 34（compileSdk）
- Android NDK 26.x+ 与 CMake 3.22.1+
- [MNN SDK](https://github.com/alibaba/MNN) — 放置到 `app/libs/mnn/`

### 构建步骤

1. 下载 MNN SDK 并放置到 `app/libs/mnn/`：

   ```
   app/libs/mnn/
     include/                # MNN 头文件（含 MNN-LLM 的 Llm.hpp）
     lib/                    # 按 ABI 划分的预编译 libMNN.so
       arm64-v8a/libMNN.so
       x86_64/libMNN.so
   ```

2. 将 Qwen MNN 模型文件放置到设备上（启动时自动检测）：

   ```
   /sdcard/Android/data/com.mongolicus/files/model/qwen.mnn
   /sdcard/Android/data/com.mongolicus/files/model/qwen_vocab.bin
   ```

   > 应用启动时会通过 `getExternalFilesDir("model")` 检查该目录并自动初始化引擎。

3. 使用 Android Studio 打开项目并构建。出于性能考虑，仅启用 64 位 ABI（`arm64-v8a`、`x86_64`）。

### 没有 MNN SDK 时的构建

项目自带了桩头文件（`app/src/main/cpp/stubs/`，包含 `MNN/Llm.hpp`、`MNN/Interpreter.hpp`、`MNN/Tensor.hpp` 与 `Stubs.cpp`），即使没有完整的 MNN SDK 也能编译通过——便于仅开发 UI。当 `app/libs/mnn/include` 不存在时，CMake 会自动回退到桩代码。要进行真正的推理，请将桩头文件替换为真实的 MNN-LLM 头文件并链接 `libMNN.so`。

## 生成参数

| 参数 | 默认值 | 范围 | 说明 |
|-----------|---------|-------|-------------|
| Temperature（温度） | 0.7 | 0 – 2 | 采样随机性 |
| Top P | 0.9 | 0 – 1 | 核采样（nucleus sampling）阈值 |
| Repetition Penalty（重复惩罚） | 1.1 | 1 – 2 | 抑制 token 重复 |
| Max Tokens（最大 token 数） | 512 | 64 – 2048 | 最多生成的 token 数量 |

## 提示词格式

使用 Qwen ChatML 格式（由 `PromptTemplate` 构造）：

```
<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
{user_message}<|im_end|>
<|im_start|>assistant
```

## 项目结构

```
mongolicus/
├── app/
│   ├── build.gradle.kts
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── cpp/
│       │   ├── CMakeLists.txt
│       │   ├── native-lib.cpp
│       │   └── stubs/MNN/          # 可选的 MNN 桩头文件
│       ├── java/com/mongolicus/
│       │   ├── MongolicusApp.kt    # Application（预加载原生库）
│       │   ├── MainActivity.kt     # 从 /model/ 自动初始化引擎
│       │   ├── engine/QwenEngine.kt
│       │   ├── data/model/ChatModels.kt
│       │   ├── data/repository/ChatRepository.kt
│       │   ├── viewmodel/ChatViewModel.kt
│       │   └── ui/                 # theme/ · screen/ · component/
│       └── res/values/             # strings.xml、themes.xml
├── build.gradle.kts
└── settings.gradle.kts
```

## 许可证

私有项目 — 保留所有权利。

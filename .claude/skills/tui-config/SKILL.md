---
name: tui-config
description: 生成、编辑、修改交错战线手游自动化脚本（JCZXAutoScript 项目）新版 Textual TUI 任务配置。当用户要新增/修改/调试 TUI 任务、添加自动化流程、配置点击/匹配/OCR/条件分支/上下文变量、拆分多文件任务、定义 method/call 复用链、或调整任务设置表单时，跳过默认方式直接使用本技能。即使没有明说"配置"或"任务"，只要涉及 jczx/Config/ 下的 .txt 配置（MainMenu.txt / tasks/*.txt / Queues.txt / Config.txt）编写，都应使用本技能。
---

# TUI 任务配置生成与编辑

本技能负责编写与维护 **JCZXAutoScript** 项目的 TUI 任务配置。配置是一组可被任务引擎执行的"实体"（section），以 `.txt` 文件存储于 `jczx/Config/`。

## 何时使用本技能

用户要让脚本**自动做某件事**（点某个按钮、识别某段文字、判断某个条件、走某条流程分支），或要**修改现有流程**时，就需要写任务配置。典型触发场景：

- "帮我加一个xxx任务 / 流程 / 自动操作"
- "这个点击为什么找不到 / 匹配失败了"
- "想按不同情况走不同分支"
- "把这个任务拆到子文件里"
- "让我能在 TUI 界面里调整某个参数"

## 工作流程

写配置前先明确目标，再选择最少的实体实现。遵循 AGENTS.md 的"简洁优先、精准修改"原则——只加完成任务所需的实体，不预造未要求的抽象。

1. **定位文件**。新任务放哪：
   - 跨任务复用的公共实体 → `MainMenu.txt`
   - 某个模块的独立任务 → `jczx/Config/tasks/<模块>.txt`
   - 可被 `type: task` 的入口通过 `type: file` 引入
   - 改某模块 → 直接编辑对应 `tasks/*.txt`
2. **读权威文档**。先读 `references/index.md`（书籍目录），按需跳到对应章节。改配置前必读相关章节，语法规则以 references 为准，**不要凭记忆想当然**。
3. **设计流程**。用 `task` 实体作为入口，`action` 串起执行链。区分"脚本必须做的判断"（condition/context）与"只是等待"（sleep/wait_target）。
4. **写实体**。每个实体一节 `[key]`，注意：
   - `key : value` 冒号分隔，**不是 `=`**
   - 逗号分隔字段**后不能加空格**（否则拆出带前导空格的项，lookup 失败）
   - 图片路径相对 `jczx/resources/`，用反斜杠（`buttons\login.png`）
5. **命名**。key 用 `类型-动作` 风格（`click-fight`、`condition-to-home`、`match-Daily`），用英文；`name` 显示名用中文。
6. **验证**。改完渲染检查：实体间引用是否都能找到、`extend` 源是否在同一文件、`target` 图片是否存在于 `jczx/resources/`、占位符 `%{}` / `${}` / `@{}` / `&{}` 引用的变量是否在链上有产出。

## 配置整体结构

```
jczx/Config/
  Config.txt      ← 全局设置（日志/线程/ADB）
  MainMenu.txt    ← 公共实体 + type: file 入口引用
  Queues.txt      ← 任务队列（[queue-xxx] 内 tasks: 列表）
  tasks/
    jjc.txt       ← 各模块任务
    receive.txt
    ...
```

## 参考文档（书籍目录）

配置规则按主题分门别类放在 `references/`，像一本书按章节组织。**先读 `references/index.md` 目录**，再跳到需要的章节。

| 章节 | 内容 | 何时读 |
|------|------|--------|
| [index.md](references/index.md) | 书籍目录与阅读指引 | 总是先读 |
| [01-syntax.md](references/01-syntax.md) | 语法、字段系统、类型总览 | 写任何实体前 |
| [02-click-match.md](references/02-click-match.md) | click / match / ocr 点击与匹配 | 做点击/识别 |
| [03-condition-context.md](references/03-condition-context.md) | condition / context 条件与变量运算 | 做分支/记录状态 |
| [04-placeholders.md](references/04-placeholders.md) | 四种占位符 `${}` `@{}` `%{}` `&{}` | 引用变量/配置 |
| [05-multifile.md](references/05-multifile.md) | 多文件拆分与 type: file | 拆分/新增任务文件 |
| [06-method-call.md](references/06-method-call.md) | method / call 复用参数化链 | 复用执行链 |
| [07-settings.md](references/07-settings.md) | 任务设置表单（settings/setting） | 配 TUI 可调参数 |
| [08-execution.md](references/08-execution.md) | 执行流程 testFor/wait_target/截图缓存 | 调试/调时序 |
| [09-func.md](references/09-func.md) | 可用 func 方法参考 | 调引擎方法 |
| [10-examples.md](references/10-examples.md) | 完整示例 | 参考写法 |

## 关键约定速记

- 字段名用 kebab-case，值不含逗号前空格。
- 列表字段（`action`/`args`/`condition_then` 等）用逗号分隔，**不加空格**。
- `match` 的 `action` 是**变换操作**（`down|1.5`），不是执行链；`context` 的 `action` 是**运算链**（`+|1`）；`dynamic` 的 `action` 是**循环源**。三者都与普通执行链语义不同，写前查对应章节。
- 图片路径用**反斜杠**，与 `resources/` 相对。
- 优先级：click 点击 `pos` > `match` > `target`；ocr 区域 `match` > `target`。
- `extend` 继承源必须**同一文件**，建议定义在子实体之前。

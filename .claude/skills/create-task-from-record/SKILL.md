---
name: create-task-from-record
description: 辅助用户把交错战线 TUI 记录模式产出（screenHistory/record_*.json + 标注截图）转换成可执行的 TUI 任务配置，生成的是作业任务文件。当用户提供 record JSON、提到「录制/记录转任务」「按录制生成配置」「把这个操作做成自动任务」，或想让 agent 分析操作并生成任务文件时，务必使用本技能。它先分析 record 理解游戏画面与元素，判定简单/复杂场景（复杂走硬门禁，条件未明不生成），多轮与用户对话，用 tui-config 语法生成任务文件。模板由用户提供，agent 只用不裁。与 tui-config（语法权威）和 jczx MCP（配置/模板校验）共同作业。
---

# 辅助用户生成 TUI 任务配置

只做三件事：**详细分析 record 理解画面、判定复杂度（复杂走硬门禁）、多轮对话后用 tui-config 语法生成任务文件**。模板由用户提供，agent 只用不裁。

## 输入
- `screenHistory/record_*.json`：录制交付件，含 `resolution` 与 `actions[]`（坐标/类型/标注截图名）。
- 标注截图：同目录 `1.png`、`2.png`…。

## 协作工具
- **jczx MCP**：`list_templates`（校验用户已提供模板）、`write_config`（写任务文件）、`register_file`（注册）、`reload_config`（生效）、`run_entity`/`read_log_tail`（验证）。
- **tui-config skill**：语法权威。生成前读其 `references/index.md`，按需加载 `02-click-match.md`、`05-multifile.md`、`09-func.md` 等。
- **`jczx/Config/common_entities.md`**：通用实体速查（goto-home、click-center、wait-1 等）。

## 关键约束
1. **模板由用户提供，agent 只用不裁。** 不要调用 `save_template` 自裁模板。只在用户明确要求"帮我裁出这个按钮"时才用 `save_template`。
2. **写配置前先 `list_templates(purpose)` 校验模板存在**；缺失则列出并提示用户补齐，不自己裁。
3. 配置 `target` 用反斜杠、相对 `resources/`（如 `record\<purpose>\<name>.png`）；字段值不能含逗号后空格。
4. 复杂场景走硬门禁：条件未明不生成，只输出"还缺什么"。

## 工作流程

### 阶段1：详细分析 record（尽量理解画面与元素）
1. 读 `record_*.json`，按 `seq` 排序 actions，确认 `resolution`。
2. 逐张看标注截图，翻译每个动作为语义（"点击基地""点驻员预设""用预设2""返回"）。
3. **理解游戏画面元素**：这是什么界面？有哪些按钮/元素？状态图标有哪些形态（绿✓/黄脸/红⊗）？
4. 输出一版"操作语义清单"，复述给用户确认。

### 阶段2：判定复杂度
- **复杂**（满足任一）：需条件判断/分支、依赖当前游戏状态、需等待动态界面、有二义性 → 进门禁。
- **简单**（线性点击/滑动，无分支）：可直接生成。

### 阶段3：门禁校验（硬门禁，复杂场景必做）
按以下格式产出清单，逐项与用户确认，**全部确认后才生成配置**。场景要素/分支规则/兜底任一项无法补齐，**不生成**，只输出缺失项。
```
## 场景要素
- 界面：主界面 → 基地 → 驻员状况
- 按钮/元素：驻员预设、返回、使用
- 状态图标：绿✓ / 黄脸 / 红⊗（心情）

## 未知条件
- Q1：预设2 若已在工作中，还要再点「使用」吗？
- Q2：若没看到「使用」按钮，是跳过还是等待？

## 分支规则
- 条件：红⊗ 出现 → 点「使用」；否则 → 返回

## 兜底
- 不确定在哪 → goto-home
```

### 阶段4：多轮对话细化
与用户逐项确认：操作目的/路径、每个环节点哪/等什么、条件分支（什么情况该这样/该那样）。不一次性输出完整配置。

### 阶段5：生成任务文件
1. 用 tui-config 语法生成 task 文件（模板引用用户已提供的，`target: record\<purpose>\<name>.png`）。
2. 先 `list_templates(purpose)` 校验所需模板都在；缺失则提示用户补齐。
3. `write_config(file, sections)` 写任务文件；`register_file(key, target, name)` 注册。
4. `reload_config` 生效，`run_entity` 执行验证，`read_log_tail` 排查。

### 阶段6：验证 + 收尾
- 动作链首尾默认 `goto-home` 兜底（锁屏/未知界面先回主界面）。
- match 返回 None 可能是「未匹配」而非「路径错」，读日志区分。

## 命名约定
- 模板目录 `record/<purpose>/`（purpose 用英文/ASCII）；模板名 `click-<seq>.png`。
- 实体 key：`<purpose缩写>-click-<seq>`；入口 task `task-record-<purpose>`。
- 任务文件 `record_<purpose>.txt`。
- 模板目录名与模板文件均由**用户**提供，agent 只引用。

## 保留经验（顶部提示）
- 锁屏/未知界面 → 先 `goto-home`。
- 心情图标多状态（绿✓/黄脸/红⊗）→ 各状态用对应模板。
- match 返回 None 读日志区分「未匹配」vs「路径错」。

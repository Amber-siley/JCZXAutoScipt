# 让 Agent 创建任务（create-task-from-record）— Design

## 背景与问题

TUI 已能录制用户操作（`screenHistory/record_*.json` + 标注截图），但把录制转成可执行任务配置曾由 `record-to-task` skill 承担，**效果未达预期**。经复盘，失败原因分两类：

**A 类：skill 引导缺失**（文档可教，非硬伤）
- 没先蒸馏用户意图、没判定复杂场景、没追问条件
- 心情图标有绿✓ / 黄脸 / 红⊗ 多状态，需对应状态模板
- 需要 `goto-home` 兜底

**B 类：MCP 工具 / 接口硬痛点**（靠写文档绕不过去，是接口设计缺位）
1. **两套目录不互通** — `save_screenshot` 写到 `<根>/template/`，但配置 `target` 读 `<根>/jczx/resources/`，agent 需手工跨目录复制，易错。
2. **路径基准不一致** — MCP `click` 相对路径基于程序根目录，config `target` 基于 `resources/`，易混。
3. **中文路径 bug** — 运行中的 TUI 对中文路径 `fm.isfile` 判定失效；而配置系统那条路径 `get_resources_target` 仍有坑。
4. **配置写入靠手工** — agent 直接编辑 `tasks/*.txt` + `MainMenu.txt`，key 冲突、`type:file` 注册、逗号空格校验全靠自觉。

## 目标（用户确认）

搭建 **MCP 工具为主 + 轻量 skill** 的工作流，让 agent 能一站式完成「看屏 → 取点 → 裁模板 → 写配置 → 注册 → 验证」闭环。

- **输入形态**：两者结合 — 既能从录制交付件批量生成，也能 agent 自主看屏 + 文字描述即席创建。
- **成果载体**：MCP 工具填平硬痛点，skill 只做轻量引导（意图理解 + 复杂场景判定 + 工具编排）。
- **末端验证**：完成后用真实录制做一次實机验证。

## 整体架构

```
agent (Claude Code)
  │ 调用 MCP 工具
  ▼
jczx/mcpServer.py (JczxMcpServer)
  ├─ save_template    → 裁图直接落 resources/record/<purpose>/
  ├─ write_config     → 复用 TxtConfig.set_config+save() 写任务文件
  └─ register_file    → 在 MainMenu 追加 type:file 注册
  │
  ▼
jczx/Config/tasks/*.txt + MainMenu.txt
  │ reload_config → run_entity → read_log_tail
  ▼
任务引擎执行
```

### Agent 典型一次闭环
```
截图看屏 → (不直接坐标点击) 用模板匹配路线
→ save_template 裁模板到 resources/record/<purpose>/
→ write_config 写任务文件 + register_file 注册 MainMenu
→ reload_config → run_entity 验证 → read_log_tail 排查
```

## 新增 MCP 工具（jczx/mcpServer.py）

用户决定：不加 `click_at`（仍走模板匹配，更稳）；保留下面三个，另将路径基准统一到 `resources/`。

### 1. `save_template(name, purpose, x1, y1, x2, y2)`
- **落盘**：`jczx/resources/record/<purpose>/<name>.png`
- 内部：`device.screenshot()` 取当前帧 → 按坐标裁切（沿用 `_do_save_screenshot` 越界裁剪逻辑）→ `imencode + open("wb")` 写盘（**不经 `cv2.imwrite`**，规避中文路径）。
- 返回 `{path, width, height}`，便于 agent 确认模板尺寸、写配置时复用。
- 需 `host.fm` 解析 `jczx/resources/` 基准；否则 `os.path.join` 基于 work_path。

### 2. `write_config(file, sections)`
- `file` 相对 `jczx/Config/tasks/`（如 `record_xxx.txt`）；`sections` 为 `{key: {field: value}}` dict。
- 内部：`TxtConfig(file_path)` → 对每 key 先查**同名冲突** → 对每 field `set_config(key, field, value)` → `save()`。
- **自动校验**：
  - 字段值含**逗号后空格** → 报错（`configEntity` 按逗号拆分）。
  - `action` / `args` 等列表字段先校验再写入。
- 返回写入的 section 数与路径。

### 3. `register_file(key, target, name)`
- 内部：检查 `menu_config` 是否已有同名 `key` → 无则 `set_config` 写 `type=file / target / name` → 只写 MainMenu 文件 → `save()`。
- 若 key 或 target 已存在 → **报错**（避免静默覆盖）。
- 注册后 agent 调 `reload_config` 生效。

### 4. 路径基准统一（`_resolve_target_path` / `_resolve_save_path`）
- `click` / `save_screenshot` 的**相对路径**解析基准改为 **`jczx/resources/`**（不再是程序根目录）。
- **保留绝对路径支持**：绝对路径仍直接使用。
- 影响：现有测试中**相对路径语义**用例需适配；绝对路径用例不受影响。

### 5. 中文路径修复
- `save_template` / `write_config` / `register_file` 内部统一二进制读写 + `np.fromfile` / `imencode`，规避 `cv2.imwrite` / `fm.isfile` 在中文路径下的失效。

## 轻量 Skill：`create-task-from-record`

改名自 `record-to-task`。坑已被 MCP 工具填平，skill 降级为**轻量引导**，只做两件事：
1. 理解用户意图 + 判定复杂场景（复杂则追问条件）
2. 协调 MCP 工具与 `tui-config` 语法文档的调用顺序

### Skill 内容流（骨架，不重复语法）
```
第 0 步：读交付件/看屏 → 明确目的（命名 purpose）
第 0.5 步：蒸馏用户行为 → 复述确认 → 判定简单/复杂（复杂则追问条件）
第 1 步：简单 → 直译每个 action 为实体；复杂 → 用 condition 分支
第 2 步：用 MCP 工具生成 + 注册：
   save_template → write_config → register_file → reload_config → run_entity → read_log_tail
第 3 步：验证 + 收尾（goto-home 兜底）
```

### 与 tui-config 协作
- `tui-config` 仍是**配置语法权威**（`references/` 索引）。
- `create-task-from-record` **不重复讲语法**，生成前读 `tui-config` 的 `references/index.md`，按需加载对应参考（`02-click-match.md`、`06-method-call.md`、`09-func.md`）。
- **保留 `jczx/Config/common_entities.md`**：精简速查（goto-home / click-center / wait-1 等），供快速引用。

### 命名约定
- 模板目录 `record/<purpose>/`（purpose 用英文/ASCII，规避中文路径）；模板名 `click-<seq>.png`。
- 实体 key：`<目的缩写>-click-<seq>`（或 `rs-` 前缀防冲突）；入口 task `task-record-<purpose>`。
- 任务文件：`record_<purpose>.txt`，经 `type:file` 注册。

### 保留的经验教训（顶部提示，不展开成冗长 FAQ）
- 锁屏 / 未知界面 → 先 `goto-home` 兜底。
- 心情图标多状态 → 用对应状态模板，不通用。
- match 返回 None 可能是「未匹配」而非「路径错」（读日志区分）。

## 测试策略

### 单元测试（`tests/engine/`，FakeDevice 桩替身，按 CLAUDE.md 硬性要求）

| 工具 | 测试要点 |
|------|----------|
| `save_template` | 裁切正确落盘；越界裁剪；中文 path 写盘成功（tmp_path 模拟）；返回 path/尺寸 |
| `write_config` | 写入任务文件字段正确；同名 section 冲突报错；逗号后空格报错；action/args 列表字段正确拆分 |
| `register_file` | 注册 type:file 到 MainMenu；重复 key 报错；注册后 `reload_config` 能加载 |

另：改造 `test_mcp_server.py` 中相对路径基准相关用例（`_resolve_target_path` 改 resources/）。

### 组装级回归测试
- `tests/engine/` 加一条：`save_template → write_config → register_file → reload_config → run_entity` 全链路，用 FakeDevice + `jczx/Config` 只读副本，验证闭环不报错、实体能执行。

## 實机验证计划

用真实录制 `screenHistory/record_20260828_210847.json` + 标注截图 323-327 走一遍：
1. `save_template` 裁 5 个模板到 `resources/record/staff_switch/`
2. `write_config` 写 `record_staff_switch.txt`
3. `register_file` 注册
4. `reload_config` → `run_entity` 执行 `rs-task-hq`
5. `read_log_tail` 排查，确认 6 步执行（goto-home→base→staff status→preset→condition→back）
6. 与上次手工成果比对，确认新工具补齐了坑

## 排除范围
- 不新增坐标点击工具（`click_at`），仍用模板匹配。
- MCP 服务的鉴权/令牌：不涉及。
- 真实 cv2 合成图匹配 / Textual TUI 测试：不涉及。

## 依赖
- 无新增 Python 依赖（复用现有 `mcp`、`cv2`、`numpy`、`TxtConfig`）。

## 文件改动清单
- `jczx/mcpServer.py`：新增 `save_template` / `write_config` / `register_file`，改 `_resolve_target_path` / `_resolve_save_path` 基准。
- `tests/engine/test_mcp_server.py`：新增 3 工具单测 + 组装级回归 + 适配基准改动。
- `.claude/skills/create-task-from-record/SKILL.md`：重写轻量引导。
- `jczx/Config/common_entities.md`：保留（速查）。
```

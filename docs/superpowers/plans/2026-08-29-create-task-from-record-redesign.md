# create-task-from-record 重设计实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `create-task-from-record` skill 重定位为「辅助用户生成 task、模板只用不裁、复杂场景硬门禁」，并新增 `list_templates` MCP 工具供 agent 写配置前校验模板存在性。

**Architecture:** 新增一个 MCP 工具 `list_templates(purpose, pattern=None)`，复用 `host.task_manage.fm` 定位 `resources/record/<purpose>/` 目录并列出 `*.png`（支持 `%substr%` 模糊匹配）。重写 SKILL.md 为新流程（分析 → 门禁 → 多轮对话 → 生成，模板只用不裁）。`write_config`/`register_file`/`save_template` 保持既有实现不变。

**Tech Stack:** Python 3.14, mcp, cv2, numpy, TxtConfig, pytest。

**Spec:** `docs/superpowers/specs/2026-08-29-create-task-from-record-redesign.md`

## Global Constraints

- Python 3.14，uv 虚拟环境，Windows-only。
- 新增特性必须配套单元测试（`tests/engine/`，桩替身，不依赖设备、不污染真实配置）。
- 路径基准：`host.task_manage.fm.work_path = <项目>/jczx`，模板目录 = `fm.join_p("resources","record",purpose)`。
- 配置 `target` 用反斜杠、相对 `jczx/resources/`；字段值不能含逗号后空格。
- `list_templates` 支持模糊匹配 `pattern` 含 `%` 子串（如 `%staff_preset%`），默认不传则列出全部 `*.png`。
- Git 提交由用户统一处理（不主动 commit）。

---

### Task 1: 新增 list_templates 工具

**Files:**
- Modify: `jczx/mcpServer.py`（注册 `list_templates` + `_do_list_templates` + `_resolve_record_dir`）
- Test: `tests/engine/test_mcp_server.py`（新增 TestListTemplates）

**Interfaces:**
- Consumes: `host.task_manage.fm`（work_path = jczx 根）。`_resolve_record_path` 已有（Task 上版实现），此处新增 `_resolve_record_dir(purpose)`。
- Produces: `list_templates(purpose: str, pattern: str | None = None) -> dict`，返回 `{"purpose": ..., "directory": ..., "templates": [...]}`。

**说明：** 列出 `resources/record/<purpose>/` 下的 `*.png`。`pattern` 为可选模糊匹配（默认不传列出全部；传 `%substr%` 只返回文件名含该子串的模板）。目录不存在返回空列表（不抛错）。

- [ ] **Step 1: 写失败测试**（`tests/engine/test_mcp_server.py` 新增 TestListTemplates）

```python
class TestListTemplates:
    """list_templates：列 resources/record/<purpose>/ 下的 png 模板，支持 %substr% 模糊匹配。"""

    def _host(self, gaming, tmp_path):
        return SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"),
                               task_manage=SimpleNamespace(fm=FakeFm(str(tmp_path))))

    def _make_dir(self, tmp_path, purpose, files):
        d = tmp_path / "resources" / "record" / purpose
        d.mkdir(parents=True, exist_ok=True)
        for f in files:
            (d / f).write_bytes(b"fake-png")
        return d

    def test_lists_all_png(self, gaming, tmp_path):
        self._make_dir(tmp_path, "sw", ["click-1.png", "click-2.png", "readme.txt", "x.png"])
        server = JczxMcpServer(self._host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        result = server._do_list_templates("sw")
        assert set(result["templates"]) == {"click-1.png", "click-2.png", "x.png"}, "应只列 png"

    def test_fuzzy_match_substr(self, gaming, tmp_path):
        self._make_dir(tmp_path, "sw", ["staff_preset_hq.png", "staff_preset_ene.png", "base.png"])
        server = JczxMcpServer(self._host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        result = server._do_list_templates("sw", pattern="%staff_preset%")
        assert set(result["templates"]) == {"staff_preset_hq.png", "staff_preset_ene.png"}

    def test_missing_dir_returns_empty(self, gaming, tmp_path):
        server = JczxMcpServer(self._host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        result = server._do_list_templates("nosuch")
        assert result["templates"] == [], "目录不存在应返回空列表而非抛错"
        assert result["directory"].endswith("nosuch")
```

- [ ] **Step 2: 运行测试确认失败**

Run: `uv run pytest tests/engine/test_mcp_server.py::TestListTemplates -v`
Expected: FAIL（`_do_list_templates` 不存在）

- [ ] **Step 3: 实现 `_do_list_templates` + `_resolve_record_dir` + 注册工具**

```python
def _do_list_templates(self, purpose: str, pattern: str = None) -> dict:
    self._logger.debug(f"MCP 工具调用 [list_templates] purpose={purpose} pattern={pattern}")
    d = self._resolve_record_dir(purpose)
    templates = []
    if os.path.isdir(d):
        for name in sorted(os.listdir(d)):
            if not name.lower().endswith(".png"):
                continue
            if pattern:
                needle = pattern.strip("%")
                if needle and needle not in name:
                    continue
            templates.append(name)
    self._logger.debug(f"MCP 工具调用 [list_templates] 完成 -> {len(templates)} 个模板 in {d}")
    return {"purpose": purpose, "directory": d, "templates": templates}

def _resolve_record_dir(self, purpose: str) -> str:
    """模板目录 = <task_manage.fm.work_path>/resources/record/<purpose>。"""
    tm = getattr(self._host, "task_manage", None)
    fm = getattr(tm, "fm", None)
    if fm is None:
        return os.path.join(os.getcwd(), "jczx", "resources", "record", purpose)
    return fm.join_p("resources", "record", purpose)
```

注册工具：

```python
@self._mcp.tool()
def list_templates(purpose: str, pattern: str | None = None) -> dict:
    """列出 jczx/resources/record/<purpose>/ 目录下的 .png 模板文件。

pattern 为可选模糊匹配（默认不传列出全部）；传如 \"%staff_preset%\" 则只返回文件名含该子串的模板。
用于写配置前确认用户已提供哪些模板、缺哪些。目录不存在返回空列表。"""
    return self._do_list_templates(purpose, pattern)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `uv run pytest tests/engine/test_mcp_server.py::TestListTemplates -v`
Expected: PASS

- [ ] **Step 5: 提交**（仅当用户指示）

---

### Task 2: 更新工具注册断言

**Files:**
- Modify: `tests/engine/test_mcp_server.py`（`TestToolRegistration.test_tools_registered`）

**Interfaces:**
- Consumes: Task 1 注册的 `list_templates`。
- Produces: 工具注册断言集合加入 `"list_templates"`。

- [ ] **Step 1: 更新断言集合** — 在 `test_tools_registered` 断言集合加入 `"list_templates"`

```python
assert names == {
    "screenshot", "click", "swipe", "drag",
    "get_resolution", "crop_screenshot", "save_screenshot", "get_screenshot_mode",
    "run_entity", "reload_config", "run_entity_json", "read_log_tail",
    "save_template", "write_config", "register_file", "list_templates",
}
```

- [ ] **Step 2: 运行测试确认通过**

Run: `uv run pytest tests/engine/test_mcp_server.py::TestToolRegistration -v`
Expected: PASS

- [ ] **Step 3: 提交**（仅当用户指示）

---

### Task 3: 重写 SKILL.md 为新流程

**Files:**
- Modify: `.claude/skills/create-task-from-record/SKILL.md`（全部重写）

**Interfaces:**
- Consumes: `list_templates`/`write_config`/`register_file`/`save_template`（限制使用）、tui-config references、common_entities.md。
- Produces: 新流程 skill，模板只用不裁、复杂场景硬门禁、多轮对话。

**说明：** 技能列表已在环境中注册（旧 SKILL.md 已存在），本任务替换其内容。frontmatter 的 `name` 保持 `create-task-from-record`，`description` 更新为「辅助用户生成 task」。

- [ ] **Step 1: 重写 `.claude/skills/create-task-from-record/SKILL.md`**

```markdown
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
```

- [ ] **Step 2: 验证技能已注册**

Run: 确认 `.claude/skills/create-task-from-record/SKILL.md` 存在且 frontmatter 正确（name=create-task-from-record）。技能列表应已含该 skill。

- [ ] **Step 3: 提交**（仅当用户指示）

---

### Task 4: 运行全部测试

**Files:**
- 无新增，仅运行。

- [ ] **Step 1: 运行 test_mcp_server.py + 组装级回归**

Run: `uv run pytest tests/engine/test_mcp_server.py tests/engine/test_create_task_workflow.py -q`
Expected: 全绿（已有测试不破坏，新增 TestListTemplates 通过）。

- [ ] **Step 2: 运行完整测试套件**

Run: `uv run pytest -q`
Expected: 182 passed + 新列表模板测试；唯一可能失败 `test_non_bool_none_result_not_written`（baseline 既有失败，与本计划无关）。

- [ ] **Step 3: 提交**（仅当用户指示）

---

## 实机验证（计划完成后手动）
用真实录制 `screenHistory/record_20260828_210847.json`：
1. `list_templates("staff_switch")` 确认用户已提供模板（用户自行放置）。
2. 生成任务文件 + 注册 + 执行验证。
3. 确认 agent 未自裁模板（只引用用户提供的）。
```

## Self-Review 结论

- **Spec 覆盖**：`list_templates`（+模糊匹配）、SKILL.md 重写、工具注册断言、测试 —— 均有对应任务。
- **占位符扫描**：无 TBD/TODO；每个 code step 有实际代码。
- **类型一致性**：`_do_list_templates(purpose, pattern)` / `_resolve_record_dir(purpose)` 在 Task 1 定义，Task 2 复用；返回结构 `{"purpose","directory","templates"}` 一致。

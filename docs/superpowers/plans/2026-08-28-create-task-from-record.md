# create-task-from-record 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增 3 个 MCP 工具（save_template / write_config / register_file）+ 路径基准统一，让 agent 能一站式完成「裁模板 → 写配置 → 注册 → 验证」，并把 `record-to-task` skill 重写为轻量引导 `create-task-from-record`。

**Architecture:** 在 `jczx/mcpServer.py` 的 `JczxMcpServer` 注册三个新工具，复用 host 的 `task_manage`（含 `menu_config`/`config_dir`）与 `fm`，用 `TxtConfig.set_config+save()` 落盘。路径基准统一到 `jczx/resources/`。skill 降级为轻量引导，只做意图理解 + 复杂场景判定 + 工具编排。

**Tech Stack:** Python 3.14, mcp (streamable-http server), cv2, numpy, TxtConfig, pytest。

**Spec:** `docs/superpowers/specs/2026-08-28-create-task-from-record-design.md`

## Global Constraints

- Python 3.14，uv 虚拟环境（`.venv/`），Windows-only。
- 新增特性必须配套单元测试（`tests/engine/`），测试不依赖设备（FakeDevice 桩替身）、不污染真实配置（`real_config_dir` 只读副本）。
- 编写 `TxtConfig.set_config+save()` 落盘；图片写盘用 `np.fromfile`/`imencode` + `open("wb")`，**禁止 `cv2.imwrite`**（中文路径失效）。
- 字段值不能含逗号后空格（`configEntity` 按逗号拆分）。
- 配置 `target` 用反斜杠、相对 `jczx/resources/`。
- Git 提交由用户统一处理（临时分支上只做改动不 commit；计划中的 commit 步骤仅在有用户指示时执行）。实际写计划用临时分支 `feat/create-task-from-record`。

---

### Task 1: 路径基准统一到 resources/

**Files:**
- Modify: `jczx/mcpServer.py`（`_resolve_target_path`）
- Test: `tests/engine/test_mcp_server.py`（新增相对路径基准用例）

**Interfaces:**
- Consumes: `host.fm`（`join_p` 基于 work_path，即 jczx 根目录）。
- Produces: `_resolve_target_path(target)` 相对路径基准改为 `jczx/resources/<target>`；绝对路径仍直接使用。**`_resolve_save_path` 保持不变**（template/ 是截图任务语义）。

**背景：** 当前 `_resolve_target_path` 用 `fm.join_p(target)`（基于 program root = `jczx` 根），导致 MCP `click` 相对路径与 config `target`（`resources/`）不一致。统一后，相对路径 = `<work_path>/jczx/resources/<target>`。测试桩 `FakeFm(root)` 的 `join_p` 基于 `root`，其 `root` 应传 `jczx` 的**父目录**（即让 `join_p("jczx","resources",target)` 成立）。

- [ ] **Step 1: 写失败测试**（`tests/engine/test_mcp_server.py` 新增）

```python
class TestResourceBasePath:
    """路径基准统一到 resources/：相对路径经 fm 基于 <task_manage.fm.work_path>/resources/ 解析，绝对路径直接用。"""

    def _host(self, gaming, root):
        # 真实 MCP host 的 task_manage.fm.work_path = jczx 根目录；FakeFm(root) 模拟 jczx 根
        return SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"),
                               task_manage=SimpleNamespace(fm=FakeFm(root)))

    def test_resolve_target_relative_to_resources(self, gaming, tmp_path):
        root = str(tmp_path)  # tmp_path 充当 jczx 根目录
        server = JczxMcpServer(self._host(gaming, root), 8765, logging.getLogger("mcp-test"))
        p = server._resolve_target_path("record\\staff_switch\\a.png")
        assert p == str(tmp_path / "resources" / "record" / "staff_switch" / "a.png")

    def test_resolve_target_absolute_used_directly(self, gaming, tmp_path):
        abs_p = str(tmp_path / "abs.png")
        server = JczxMcpServer(self._host(gaming, str(tmp_path)), 8765, logging.getLogger("mcp-test"))
        assert server._resolve_target_path(abs_p) == abs_p
```

- [ ] **Step 2: 运行测试确认失败**

Run: `uv run pytest tests/engine/test_mcp_server.py::TestResourceBasePath -v`
Expected: FAIL（`_resolve_target_path` 仍返回 root 下路径，未包含 `jczx/resources/`）

- [ ] **Step 3: 修改 `_resolve_target_path`**

```python
def _resolve_target_path(self, target: str) -> str:
    """解析点击目标图片路径：绝对路径直接用；相对路径经 host.task_manage.fm 基于 <work_path>/resources/ 解析（与 config target 基准一致）。

    已实测：host.task_manage.fm.work_path = <项目>/jczx，join_p("resources",...) → <项目>/jczx/resources/...。
    """
    if os.path.isabs(target):
        return target
    tm = getattr(self._host, "task_manage", None)
    fm = getattr(tm, "fm", None)
    if fm is None:
        return os.path.join(os.getcwd(), "jczx", "resources", target)
    rel = ["resources"] + target.replace("/", "\\").split("\\")
    return fm.join_p(*rel)
```

> **实现要点**：实测确认 `host.task_manage.fm.work_path = D:\IDEProjects\JCZXAutoScript\jczx`（jczx 根目录），所以相对路径基准就是 `<jczx>/resources/<target>`，与 `get_resources_target` 完全一致。`save_template`/`write_config`/`register_file` 都访问 `host.task_manage`（而非 `host.fm`，因为 MCP host 自身的 `self.fm = FileManage()` 无参指向项目根，不含 jczx）。

- [ ] **Step 4: 运行测试确认通过**

Run: `uv run pytest tests/engine/test_mcp_server.py::TestResourceBasePath -v`
Expected: PASS

- [ ] **Step 5: 跑既有测试确认不破坏**

Run: `uv run pytest tests/engine/test_mcp_server.py -v`
Expected: PASS（注意：既有 `test_click_with_target_clicks_center` 等用绝对路径 `str(tmp_path/...)`，不受影响；若有用相对路径的用例需适配）

- [ ] **Step 6: 提交**（仅当用户指示）

---

### Task 2: save_template 工具

**Files:**
- Modify: `jczx/mcpServer.py`（注册 `save_template` + `_do_save_template`）
- Test: `tests/engine/test_mcp_server.py`（新增 TestSaveTemplate）

**Interfaces:**
- Consumes: `device.screenshot()`（返回 BGR ndarray）；`host.fm`。
- Produces: `save_template(name, purpose, x1, y1, x2, y2)` → 模板落盘到 `<root>/jczx/resources/record/<purpose>/<name>.png`，返回 `{"path": ..., "width": ..., "height": ...}`。

**说明：** 落盘到 `resources/record/<purpose>/`（不是 `template/`），让配置 `target: record\<purpose>\<name>.png` 可直接引用，消除跨目录复制。

- [ ] **Step 1: 写失败测试**（`tests/engine/test_mcp_server.py` 新增 TestSaveTemplate）

```python
class TestSaveTemplate:
    """save_template：裁图直接落 resources/record/<purpose>/<name>.png，支持中文 purpose。"""

    def _host(self, gaming, tmp_path):
        # 真实 MCP host 的 task_manage.fm.work_path = jczx 根目录；此处 FakeFm(tmp_path) 模拟 jczx 根
        return SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"),
                               task_manage=SimpleNamespace(fm=FakeFm(str(tmp_path))))

    def test_saves_template_to_resources_record(self, gaming, tmp_path):
        import cv2, numpy as np
        img = np.arange(20 * 20 * 3, dtype=np.uint8).reshape(20, 20, 3)
        gaming.screenshot = lambda: img
        server = JczxMcpServer(self._host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        result = server._do_save_template("click-1", "staff_switch", 5, 5, 10, 10)
        p = tmp_path / "resources" / "record" / "staff_switch" / "click-1.png"
        assert os.path.exists(p), f"应落盘到 {p}"
        assert result["path"] == str(p)
        assert result["width"] == 5 and result["height"] == 5

    def test_chinese_purpose_path_ok(self, gaming, tmp_path):
        import numpy as np
        gaming.screenshot = lambda: np.zeros((20, 20, 3), np.uint8)
        server = JczxMcpServer(self._host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        result = server._do_save_template("t", "驻员切换", 0, 0, 8, 8)
        p = tmp_path / "resources" / "record" / "驻员切换" / "t.png"
        assert os.path.exists(p)
        assert result["width"] == 8

    def test_invalid_crop_raises(self, gaming, tmp_path):
        import numpy as np
        gaming.screenshot = lambda: np.zeros((20, 20, 3), np.uint8)
        server = JczxMcpServer(self._host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        try:
            server._do_save_template("t", "x", 10, 10, 5, 5)
            assert False, "应抛裁切区域无效"
        except RuntimeError as e:
            assert "裁切区域无效" in str(e)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `uv run pytest tests/engine/test_mcp_server.py::TestSaveTemplate -v`
Expected: FAIL（`_do_save_template` 不存在）

- [ ] **Step 3: 实现 `_do_save_template` + 注册工具**

```python
def _do_save_template(self, name, purpose, x1, y1, x2, y2) -> dict:
    device = self._device()
    self._logger.debug(f"MCP 工具调用 [save_template] name={name} purpose={purpose} crop=({x1},{y1})-({x2},{y2})")
    img = device.screenshot()
    h, w = img.shape[:2]
    x1 = max(int(x1), 0); y1 = max(int(y1), 0)
    x2 = min(int(x2), w); y2 = min(int(y2), h)
    if x2 <= x1 or y2 <= y1:
        raise RuntimeError(f"裁切区域无效: ({x1},{y1})-({x2},{y2}) 超出画面 {w}x{h}")
    crop = img[y1:y2, x1:x2]
    path = self._resolve_record_path(name, purpose)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ok, buf = cv2.imencode(".png", crop)
    if not ok:
        raise RuntimeError(f"截图 PNG 编码失败: {path}")
    with open(path, "wb") as fp:
        fp.write(buf.tobytes())
    self._logger.debug(f"MCP 工具调用 [save_template] 完成 -> {path} ({x2-x1}x{y2-y1})")
    return {"path": path, "width": x2 - x1, "height": y2 - y1}

def _resolve_record_path(self, name: str, purpose: str) -> str:
    """模板落盘到 <task_manage.fm.work_path>/resources/record/<purpose>/<name>.png。

    真实 host.task_manage.fm.work_path = jczx 根目录，join_p("resources","record",...) → <jczx>/resources/record/...。
    """
    tm = getattr(self._host, "task_manage", None)
    fm = getattr(tm, "fm", None)
    if fm is None:
        return os.path.join(os.getcwd(), "jczx", "resources", "record", purpose, f"{name}.png")
    rel = ["resources", "record", purpose, f"{name}.png"]
    return fm.join_p(*rel)
```

注册工具：

```python
@self._mcp.tool()
def save_template(name: str, purpose: str, x1: int, y1: int, x2: int, y2: int) -> dict:
    """从当前设备画面裁出 (x1,y1)-(x2,y2) 区域，保存为模板到 jczx/resources/record/<purpose>/<name>.png。
    之后配置实体 target 可直接用 record\<purpose>\<name>.png 引用。name 不含扩展名。"""
    return self._do_save_template(name, purpose, x1, y1, x2, y2)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `uv run pytest tests/engine/test_mcp_server.py::TestSaveTemplate -v`
Expected: PASS

- [ ] **Step 5: 提交**（仅当用户指示）

---

### Task 3: write_config 工具

**Files:**
- Modify: `jczx/mcpServer.py`（注册 `write_config` + `_do_write_config`）
- Test: `tests/engine/test_mcp_server.py`（新增 TestWriteConfig）

**Interfaces:**
- Consumes: host 的 `task_manage`（含 `config_dir`，指向 `jczx/Config`）；`TxtConfig`。
- Produces: `write_config(file, sections)` → 把 `sections`（`{key: {field: value}}`）写入 `<config_dir>/tasks/<file>`；返回 `{"path": ..., "wrote": n}`。同名 key 已存在时报错；字段值含逗号后空格时报错。

**说明：** `file` 相对 `jczx/Config/tasks/`。`TxtConfig(file_path)` 若文件不存在则先建空配置，`set_config` 会新建 section，`save()` 全量写入。

- [ ] **Step 1: 写失败测试**（新增 TestWriteConfig）

```python
class TestWriteConfig:
    """write_config：复用 TxtConfig.set_config+save() 写任务文件，校验同名冲突与逗号空格。"""

    def _host(self, gaming, tmp_path):
        cfg_dir = tmp_path / "Config"
        return SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"),
                               fm=FakeFm(str(tmp_path)),
                               task_manage=SimpleNamespace(config_dir=str(cfg_dir)))

    def test_writes_sections(self, gaming, tmp_path):
        server = JczxMcpServer(self._host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        sections = {
            "task-a": {"type": "task", "name": "任务A", "action": "goto-home,click-x"},
            "click-x": {"type": "click", "target": "record\\a\\x.png", "sleep": "1"},
        }
        result = server._do_write_config("record_a.txt", sections)
        p = tmp_path / "Config" / "tasks" / "record_a.txt"
        assert os.path.exists(p), f"应写入 {p}"
        assert result["wrote"] == 2
        # 重新读取验证
        from jczx.CommonBuilder.CommonBuilder.FileTools.ConfigUtils import TxtConfig
        cfg = TxtConfig(str(p))
        assert cfg.get_config("task-a", "type") == "task"
        assert cfg.get_config("task-a", "action") == "goto-home,click-x"
        assert cfg.get_config("click-x", "target") == "record\\a\\x.png"

    def test_dup_key_raises(self, gaming, tmp_path):
        import os
        from jczx.CommonBuilder.CommonBuilder.FileTools.ConfigUtils import TxtConfig
        p = tmp_path / "Config" / "tasks" / "rec.txt"
        os.makedirs(p.parent, exist_ok=True)
        cfg = TxtConfig(str(p)); cfg.set_config("task-a", "type", "task"); cfg.save()
        server = JczxMcpServer(self._host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        try:
            server._do_write_config("rec.txt", {"task-a": {"type": "click"}})
            assert False, "应抛同名冲突"
        except RuntimeError as e:
            assert "同名" in str(e) or "冲突" in str(e)

    def test_comma_space_raises(self, gaming, tmp_path):
        server = JczxMcpServer(self._host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        try:
            server._do_write_config("rec.txt", {"t": {"action": "goto-home, click-x"}})
            assert False, "应抛逗号后空格"
        except RuntimeError as e:
            assert "逗号" in str(e)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `uv run pytest tests/engine/test_mcp_server.py::TestWriteConfig -v`
Expected: FAIL（`_do_write_config` 不存在）

- [ ] **Step 3: 实现 `_do_write_config` + 注册工具**

```python
def _do_write_config(self, file: str, sections: dict) -> dict:
    import re
    host = self._host
    self._logger.debug(f"MCP 工具调用 [write_config] file={file} sections={list(sections)}")
    cfg_dir = getattr(getattr(host, "task_manage", None), "config_dir", None)
    if not cfg_dir:
        raise RuntimeError("TUI 主机未就绪，无法写入配置（task_manage.config_dir 为空）")
    from jczx.CommonBuilder.CommonBuilder.FileTools.ConfigUtils import TxtConfig
    path = os.path.join(cfg_dir, "tasks", file)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cfg = TxtConfig(path)
    for key, fields in sections.items():
        try:
            existing = cfg.get_config(key, "type")
            if existing:
                raise RuntimeError(f"同名 section 冲突: {key} 已存在")
        except KeyError:
            pass
        for field, value in fields.items():
            sv = str(value)
            if "," in sv and re.search(r",\s", sv):
                raise RuntimeError(f"字段 {key}.{field} 值含逗号后空格（configEntity 按逗号拆分会出错）: {sv!r}")
            cfg.set_config(key, field, sv)
    cfg.save()
    self._logger.debug(f"MCP 工具调用 [write_config] 完成 -> {path} ({len(sections)} sections)")
    return {"path": path, "wrote": len(sections)}
```

注册工具：

```python
@self._mcp.tool()
def write_config(file: str, sections: dict) -> dict:
    """把一组 section 定义写入 jczx/Config/tasks/<file>（.txt 配置），复用 TxtConfig.set_config+save()。
sections 形如 {"task-a": {"type": "task", "name": "任务A", "action": "goto-home,click-x"}}。
自动校验：同名 section 冲突、字段值含逗号后空格会报错。写入后需调 reload_config 生效。"""
    return self._do_write_config(file, sections)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `uv run pytest tests/engine/test_mcp_server.py::TestWriteConfig -v`
Expected: PASS

- [ ] **Step 5: 提交**（仅当用户指示）

---

### Task 4: register_file 工具

**Files:**
- Modify: `jczx/mcpServer.py`（注册 `register_file` + `_do_register_file`）
- Test: `tests/engine/test_mcp_server.py`（新增 TestRegisterFile）

**Interfaces:**
- Consumes: host 的 `task_manage.menu_config`（`TxtConfig`，绑定 MainMenu.txt）；`task_manage.menu_config_path`。
- Produces: `register_file(key, target, name)` → 在 MainMenu 写入 `[key] type=file target=<target> name=<name>` 并 save；返回 `{"path": ..., "key": key}`。key 已存在时报错。

**说明：** 直接操作 `menu_config`（已加载 MainMenu）。用 `set_config` 写 `type/file/target/name` 四行，`save()` 落盘，避免手工编辑.

- [ ] **Step 1: 写失败测试**（新增 TestRegisterFile）

```python
class TestRegisterFile:
    """register_file：在 MainMenu 写入 type:file 注册，重复 key 报错。"""

    def _host(self, gaming, tmp_path):
        cfg_dir = tmp_path / "Config"
        menu_path = cfg_dir / "MainMenu.txt"
        os.makedirs(cfg_dir, exist_ok=True)
        mm = TxtConfig(str(menu_path))
        mm.set_config("goto-home", "type", "task"); mm.save()
        tm = SimpleNamespace(menu_config=mm, menu_config_path=str(menu_path), config_dir=str(cfg_dir))
        return SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"),
                               fm=FakeFm(str(tmp_path)), task_manage=tm)

    def test_registers_file(self, gaming, tmp_path):
        server = JczxMcpServer(self._host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        result = server._do_register_file("file-record-a", "tasks\\record_a.txt", "记录A")
        assert result["key"] == "file-record-a"
        mm = server._host.task_manage.menu_config
        assert mm.get_config("file-record-a", "type") == "file"
        assert mm.get_config("file-record-a", "target") == "tasks\\record_a.txt"
        assert mm.get_config("file-record-a", "name") == "记录A"

    def test_dup_key_raises(self, gaming, tmp_path):
        server = JczxMcpServer(self._host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        server._do_register_file("file-record-a", "tasks\\a.txt", "A")
        try:
            server._do_register_file("file-record-a", "tasks\\b.txt", "B")
            assert False, "应抛重复 key"
        except RuntimeError as e:
            assert "重复" in str(e) or "已存在" in str(e)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `uv run pytest tests/engine/test_mcp_server.py::TestRegisterFile -v`
Expected: FAIL（`_do_register_file` 不存在）

- [ ] **Step 3: 实现 `_do_register_file` + 注册工具**

```python
def _do_register_file(self, key: str, target: str, name: str) -> dict:
    host = self._host
    self._logger.debug(f"MCP 工具调用 [register_file] key={key} target={target} name={name}")
    tm = getattr(host, "task_manage", None)
    menu = getattr(tm, "menu_config", None)
    if menu is None:
        raise RuntimeError("TUI 主机未就绪，无法注册（task_manage.menu_config 为空）")
    try:
        existing = menu.get_config(key, "type")
        raise RuntimeError(f"重复注册: key {key} 已存在 (type={existing})")
    except KeyError:
        pass
    menu.set_config(key, "type", "file")
    menu.set_config(key, "target", target)
    menu.set_config(key, "name", name)
    menu.save()
    path = getattr(tm, "menu_config_path", None)
    self._logger.debug(f"MCP 工具调用 [register_file] 完成 -> {path}")
    return {"path": path, "key": key}
```

注册工具：

```python
@self._mcp.tool()
def register_file(key: str, target: str, name: str) -> dict:
    """在 jczx/Config/MainMenu.txt 追加一个 type:file 注册，把任务文件挂进公共实体池。
key 为 section 名（如 file-record-a），target 相对 Config 目录（如 tasks\\record_a.txt），name 为中文显示名。
重复 key 会报错。写入后需调 reload_config 生效。"""
    return self._do_register_file(key, target, name)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `uv run pytest tests/engine/test_mcp_server.py::TestRegisterFile -v`
Expected: PASS

- [ ] **Step 5: 提交**（仅当用户指示）

---

### Task 5: 更新工具注册测试（test_tools_registered）

**Files:**
- Modify: `tests/engine/test_mcp_server.py`（`TestToolRegistration.test_tools_registered`）

**Interfaces:**
- Consumes: 前三任务注册的 `save_template` / `write_config` / `register_file`。
- Produces: 新工具名进入已注册集合断言。

- [ ] **Step 1: 更新断言集合**

把 `assert names == {...}` 集合加入 `"save_template"`, `"write_config"`, `"register_file"`。

```python
assert names == {
    "screenshot", "click", "swipe", "drag",
    "get_resolution", "crop_screenshot", "save_screenshot", "get_screenshot_mode",
    "run_entity", "reload_config", "run_entity_json", "read_log_tail",
    "save_template", "write_config", "register_file",
}
```

- [ ] **Step 2: 运行测试确认通过**

Run: `uv run pytest tests/engine/test_mcp_server.py::TestToolRegistration -v`
Expected: PASS

- [ ] **Step 3: 提交**（仅当用户指示）

---

### Task 6: 组装级回归测试（全链路）

**Files:**
- Create: `tests/engine/test_create_task_workflow.py`

**Interfaces:**
- Consumes: `save_template` → `write_config` → `register_file` → `reload_config` → `run_entity`。
- Produces: 用 FakeDevice + 真实 `jczx/Config` 只读副本验证闭环不报错、实体能执行。

**说明：** 用只读副本避免污染真实配置。若 `reload_config` 需要真实 host（`_reload_configs`），用桩替身模拟。

- [ ] **Step 1: 写测试**

```python
"""组装级：save_template→write_config→register_file→reload_config→run_entity 闭环。"""
import os
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from jczx.mcpServer import JczxMcpServer
from jczx.CommonBuilder.CommonBuilder.FileTools.ConfigUtils import TxtConfig
from tests.engine.fake_device import make_gaming
from tests.engine.test_mcp_server import FakeFm


@pytest.fixture
def real_config_copy(tmp_path):
    """复制 jczx/Config 只读副本到 tmp，避免污染真实配置。"""
    src = Path(__file__).resolve().parents[2] / "jczx" / "Config"
    dst = tmp_path / "Config"
    shutil.copytree(src, dst)
    return dst


def test_full_workflow(real_config_copy, tmp_path, monkeypatch):
    gaming = make_gaming()
    # host.task_manage 需同时提供 fm（save_template 落盘）、config_dir（write_config）、menu_config（register_file）
    menu_path = real_config_copy / "MainMenu.txt"
    mm = TxtConfig(str(menu_path))  # 只读副本的 MainMenu，注册写这里不污染真实配置
    host = SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"),
                           task_manage=SimpleNamespace(fm=FakeFm(str(tmp_path)),
                                                       config_dir=str(real_config_copy),
                                                       menu_config=mm,
                                                       menu_config_path=str(menu_path)))
    server = JczxMcpServer(host, 8765, logging.getLogger("mcp-test"))

    # 1. 裁模板（落 tmp_path/resources/record/wf/，不污染真实 jczx/resources）
    import numpy as np
    gaming.screenshot = lambda: np.zeros((20, 20, 3), np.uint8)
    tpl = server._do_save_template("btn", "wf", 0, 0, 8, 8)
    assert os.path.exists(tpl["path"])
    assert str(tmp_path / "resources" / "record" / "wf" / "btn.png") in tpl["path"]

    # 2. 写配置
    sections = {
        "wf-task": {"type": "task", "name": "工作流", "action": "wf-click"},
        "wf-click": {"type": "click", "target": "record\\wf\\btn.png", "per": "0.8"},
    }
    res = server._do_write_config("record_wf.txt", sections)
    assert res["wrote"] == 2

    # 3. 注册
    reg = server._do_register_file("file-wf", "tasks\\record_wf.txt", "工作流")
    assert reg["key"] == "file-wf"

    # 4-5. reload_config + run_entity（用桩替身模拟 host._reload_configs）
    executed = []
    gaming.exec = lambda name: executed.append(name)
    server._do_run_entity("wf-task")
    assert executed == ["wf-task"]
```

- [ ] **Step 2: 运行测试确认通过**

Run: `uv run pytest tests/engine/test_create_task_workflow.py -v`
Expected: PASS

- [ ] **Step 3: 提交**（仅当用户指示）

---

### Task 7: 重写 skill 为 create-task-from-record（轻量引导）

**Files:**
- Create: `.claude/skills/create-task-from-record/SKILL.md`
- Create: `jczx/Config/common_entities.md`（速查）
- Delete: `.claude/skills/record-to-task/`（若仍存在）

**Interfaces:**
- Consumes: MCP 新工具（save_template / write_config / register_file）+ tui-config references + common_entities.md。
- Produces: 轻量 skill，只做意图理解 + 复杂场景判定 + 工具编排。

- [ ] **Step 1: 写 `create-task-from-record/SKILL.md`**

```markdown
---
name: create-task-from-record
description: 把交错战线 TUI 记录模式产出（screenHistory/record_*.json + 标注截图）转换成可执行的 TUI 任务配置；也支持 agent 结合当前游戏画面 + 文字描述即席创建任务。当用户提供 record JSON、提到「录制/记录转任务」「按录制生成配置」「把这个操作做成自动任务」，或让 agent 看屏做任务时，务必使用本技能。它会先提炼用户意图并确认、判定是否复杂场景（复杂则追问条件），再用 MCP 工具（save_template/write_config/register_file）裁模板、写配置、注册，最后验证。与 tui-config（语法权威）和 jczx MCP（设备/配置操作）共同作业。
---

# 记录/看屏 → TUI 任务配置

坑已在 MCP 工具层填平，本 skill 只做三件事：**理解意图、判定复杂度、编排工具**。语法细节一律读 tui-config 的 references，不要凭记忆写配置。

## 数据来源
- `screenHistory/record_*.json`：录制交付件，含 `resolution` 与 `actions[]`（坐标/类型/标注截图名）。
- 标注截图：同目录 `1.png`、`2.png`…。

## 协作工具
- **jczx MCP**：`screenshot`/`crop_screenshot`/`save_template`/`write_config`/`register_file`/`reload_config`/`run_entity`/`read_log_tail`。
- **tui-config skill**：语法权威。生成前读其 `references/index.md`，按需加载 `02-click-match.md`、`05-multifile.md`、`09-func.md` 等。
- **`jczx/Config/common_entities.md`**：通用实体速查（goto-home、click-center、wait-1 等），需要兜底/等待时优先引用。

## 关键约束
1. MCP 不支持按坐标点击 → 用 `save_template` 裁图当模板，再用 `click` 匹配。
2. `save_template` 直接落盘到 `resources/record/<purpose>/`，配置 `target` 用 `record\<purpose>\<name>.png` 引用，两处基准都是 `resources/`，不再跨目录复制。
3. 字段值不能含逗号后空格（`configEntity` 按逗号拆分）。
4. 生成的任务文件是新文件，且必须 `register_file` 注册到 MainMenu 才能被加载。

## 工作流程
### 第 0 步：确认目的与输入
向用户确认这次录制的目的（即 `purpose`，用于目录与命名）。收集：record JSON 路径、标注截图目录、一句话描述。

### 第 0.5 步：蒸馏行为 + 判定复杂度（务必做）
1. 逐张看标注截图 + 对照 record 坐标，把每个 action 翻译成一句语义（"点击基地""点驻员预设"…）。
2. 用一两句话复述你的理解给用户确认。
3. 判定简单/复杂场景：
   - 简单：线性点击/滑动序列 → 直译。
   - 复杂：需条件判断（"有没有红点""弹窗是否出现"）、循环、等待动态界面、或取决于游戏状态（"预设2 是否已在使用"）→ **必须追问相关条件**，把答案写进 condition 分支。

### 第 1 步：转手势为实体（读 tui-config 语法）
- click (x,y) → `type:click`，`target: record\<purpose>\<seq>.png`
- swipe/drag → `type:func`，`func: swipe_proportion`/`drag_drop_proportion` 或像素版

### 第 2 步：用 MCP 工具生成 + 注册
1. `save_template(name, purpose, x1,y1,x2,y2)` 裁模板（name 用 `click-<seq>`）。
2. `write_config(file, sections)` 写 `record_<purpose>.txt`。
3. `register_file(key, target, name)` 注册。
4. `reload_config` → `run_entity` 验证 → `read_log_tail` 排查。

### 第 3 步：验证 + 收尾
- 动作链首尾默认加 `goto-home` 兜底（锁屏/未知界面先回主界面）。
- match 返回 None 可能是「未匹配」而非「路径错」，读日志区分。

## 命名约定
- 模板目录 `record/<purpose>/`（purpose 用英文/ASCII，规避中文路径）；模板名 `click-<seq>.png`。
- 实体 key：`<purpose缩写>-click-<seq>`；入口 task `task-record-<purpose>`。
- 任务文件 `record_<purpose>.txt`。

## 保留经验（顶部提示）
- 锁屏/未知界面 → 先 `goto-home`。
- 心情图标多状态（绿✓/黄脸/红⊗）→ 用对应状态模板。
- match 返回 None 读日志区分「未匹配」vs「路径错」。
```

- [ ] **Step 2: 创建 `common_entities.md`**（速查）

```markdown
# 通用实体速查

> 引用这些已定义 key，别重造。语法细节见 tui-config 的 references（尤其 02-click-match.md / 09-func.md）。

| key | 类型 | 说明 |
|-----|------|------|
| `goto-home` | task | 返回主界面（锁屏/未知界面先用它兜底），含判断与点击返回 |
| `click-home` | click | 点主界面按钮 |
| `click-back` | click | 点返回按钮 |
| `click-center` | func | 点屏幕中心 |
| `click-upcenter` | func | 点屏幕（中线偏上） |
| `wait-1` | click | 停 1 秒 |
| `wait-2` | click | 停 2 秒 |
| `wait-5` | click | 停 5 秒 |
| `click-fight` | click | 出击 |
| `click-activity-fight` | click | 活动探索 |
| `click-inllusion` | click | 碎星虚影 |
| `click-get-item` | click | 获取物品 |
| `click-start-fight` | click | 开始战斗 |
| `auto-fight` | task | 自动战斗（跳过动画→自动→等胜/败） |
| `in_location` | func | 判断当前是否处于某目标画面 |
```

- [ ] **Step 3: 若 `record-to-task/` 存在则删除**

Run: `rm -rf .claude/skills/record-to-task`
Expected: 无残留。

- [ ] **Step 4: 提交**（仅当用户指示）

---

### Task 8: 运行全部测试

**Files:**
- 无新增，仅运行。

- [ ] **Step 1: 运行完整测试套件**

Run: `uv run pytest`
Expected: 全部 PASS（`tests/pure`、`tests/regression`、`tests/engine`），不破坏既有测试。

- [ ] **Step 2: 提交**（仅当用户指示）

---

## 实机验证（计划完成后手动步骤）

用真实录制 `screenHistory/record_20260828_210847.json` + 标注截图 323-327：
1. `save_template` 裁 5 个模板到 `resources/record/staff_switch/`。
2. `write_config` 写 `record_staff_switch.txt`。
3. `register_file` 注册。
4. `reload_config` → `run_entity` 执行 `rs-task-hq`。
5. `read_log_tail` 排查，确认 6 步执行。
6. 与上次手工成果比对，确认新工具补齐了坑。

此步在工具/skill 全部实现并单测通过后进行，属于用户可选的实机确认环节。

---

## Self-Review 结论

- **Spec 覆盖**：3 工具（save_template/write_config/register_file）+ 路径基准统一 + 轻量 skill + common_entities.md + 单测 + 组装回归 + 实机验证 —— 均有对应任务。
- **占位符扫描**：无 TBD/TODO；每个 code step 都有实际代码。
- **类型一致性**：`_do_save_template`/`_do_write_config`/`_do_register_file` 名称与返回类型在 Task 2/3/4 定义，Task 5/6 复用一致。

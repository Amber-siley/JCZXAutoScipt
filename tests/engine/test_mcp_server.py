"""方案 2（引擎级）：JczxMcpServer — 4 个设备工具注册与行为。

host 桩替身：SimpleNamespace(device=make_gaming(...), logger=...)。
复用 fake_device 的 make_gaming（object.__new__ 绕过 ADB）。
"""
import asyncio
import logging
import os
from types import SimpleNamespace

from jczx.jczxCli import JczxCli
from jczx.mcpServer import JczxMcpServer


def make_host(gaming):
    return SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"))


class FakeFm:
    """FileManage 替身：join_p 基于 work_path 拼接（对应真实 fm.join_p → work_path/template）。"""

    def __init__(self, work_path):
        self.work_path = str(work_path)

    def join_p(self, *args):
        return os.path.join(self.work_path, *args)


def make_save_host(gaming, tmp_path):
    return SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"),
                           fm=FakeFm(tmp_path))


class TestToolRegistration:
    def test_tools_registered(self, gaming):
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        names = {t.name for t in asyncio.run(server._mcp.list_tools())}
        assert names == {
            "screenshot", "click", "swipe", "drag",
            "get_resolution", "crop_screenshot", "save_screenshot", "get_screenshot_mode",
            "run_entity", "reload_config", "run_entity_json", "read_log_tail",
            "save_template", "write_config", "register_file", "list_templates",
        }


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


class TestDeviceOps:
    def test_click_with_target_clicks_center(self, gaming, tmp_path):
        import cv2
        import numpy as np
        p = str(tmp_path / "btn.png")
        cv2.imwrite(p, np.zeros((20, 20), np.uint8))
        gaming.findImageCenterLocations = lambda img, per=0.8, cutPoints=None, grayScreenshot=None: [(30, 40)]
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        result = server._do_click(target=p)
        assert "已点击目标" in result and "(30, 40)" in result
        assert gaming.clicks == [(30, 40)], "应点击模板匹配的中心点"

    def test_click_with_target_not_found_raises(self, gaming, tmp_path):
        import cv2
        import numpy as np
        p = str(tmp_path / "btn.png")
        cv2.imwrite(p, np.zeros((20, 20), np.uint8))
        gaming.findImageCenterLocations = lambda img, per=0.8, cutPoints=None, grayScreenshot=None: []
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        try:
            server._do_click(target=p)
            assert False, "应抛未匹配"
        except RuntimeError as e:
            assert "未匹配到目标" in str(e)

    def test_click_with_bad_target_raises(self, gaming):
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        try:
            server._do_click(target="nonexistent\\path.png")
            assert False, "应抛无法加载"
        except RuntimeError as e:
            assert "无法加载" in str(e)

    def test_swipe_calls_device(self, gaming):
        gaming.swipes = []
        gaming.swipe = lambda x1, y1, x2, y2, duration: gaming.swipes.append((x1, y1, x2, y2, duration))
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        assert server._do_swipe(0, 0, 100, 200) == "已滑动 (0,0) -> (100,200)"
        assert gaming.swipes == [(0, 0, 100, 200, 200)]

    def test_drag_calls_device(self, gaming):
        gaming.drags = []
        gaming.dragAndDrop = lambda x1, y1, x2, y2, duration: gaming.drags.append((x1, y1, x2, y2, duration))
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        assert server._do_drag(1, 2, 3, 4, 500) == "已拖动 (1,2) -> (3,4)"
        assert gaming.drags == [(1, 2, 3, 4, 500)]

    def test_screenshot_returns_png_image(self, gaming):
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        img = server._do_screenshot()
        assert img.data[:8] == b"\x89PNG\r\n\x1a\n"  # PNG 魔数
        assert img._format == "png"  # mcp v2.0.0 Image 将 format 存为私有 _format

    def test_get_resolution_returns_device_size(self, gaming):
        gaming.size = (2400, 1080)
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        assert server._do_get_resolution() == {"width": 2400, "height": 1080}

    def test_crop_screenshot_returns_cropped_png(self, gaming):
        import cv2
        import numpy as np
        img = np.arange(20 * 20 * 3, dtype=np.uint8).reshape(20, 20, 3)
        gaming.screenshot = lambda: img
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        out = server._do_crop_screenshot(5, 5, 10, 10)
        assert out._format == "png"
        dec = cv2.imdecode(np.frombuffer(out.data, np.uint8), cv2.IMREAD_COLOR)
        assert dec.shape == (5, 5, 3), f"应裁出 5x5，实际 {dec.shape}"
        assert (dec == img[5:10, 5:10]).all(), "裁切内容应与原图对应区域一致"

    def test_crop_screenshot_clips_to_bounds(self, gaming):
        import cv2
        import numpy as np
        gaming.screenshot = lambda: np.zeros((20, 20, 3), np.uint8)
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        out = server._do_crop_screenshot(-5, -5, 100, 100)
        dec = cv2.imdecode(np.frombuffer(out.data, np.uint8), cv2.IMREAD_COLOR)
        assert dec.shape == (20, 20, 3), "越界坐标应裁剪到画面范围"


class TestErrors:
    def test_device_not_connected_raises(self):
        host = SimpleNamespace(device=None, logger=logging.getLogger("mcp-test"))
        server = JczxMcpServer(host, 8765, logging.getLogger("mcp-test"))
        try:
            server._do_click(1, 1)
            assert False, "应抛设备未连接"
        except RuntimeError as e:
            assert "设备未连接" in str(e)

    def test_get_resolution_unknown_raises(self, gaming):
        gaming.size = None  # 设备无分辨率信息
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        try:
            server._do_get_resolution()
            assert False, "应抛设备分辨率未知"
        except RuntimeError as e:
            assert "设备分辨率未知" in str(e)

    def test_crop_screenshot_invalid_region_raises(self, gaming):
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        try:
            server._do_crop_screenshot(10, 10, 5, 5)  # x2 < x1
            assert False, "应抛裁切区域无效"
        except RuntimeError as e:
            assert "裁切区域无效" in str(e)


class TestBusyWarning:
    def test_busy_warns_but_executes(self, gaming, caplog, tmp_path):
        import cv2
        import numpy as np
        p = str(tmp_path / "btn.png")
        cv2.imwrite(p, np.zeros((20, 20), np.uint8))
        gaming._exec_mgr = SimpleNamespace(is_running=lambda: True, token=gaming.token)
        gaming.findImageCenterLocations = lambda img, per=0.8, cutPoints=None, grayScreenshot=None: [(5, 5)]
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        with caplog.at_level(logging.WARNING, logger="mcp-test"):
            server._do_click(p)
        assert gaming.clicks == [(5, 5)], "应照常执行"
        assert any("任务执行期间" in r.message for r in caplog.records)


class TestDebugLogging:
    """MCP 工具调用应输出 debug 日志（工具名 + 参数 + 结果）。"""

    def test_tool_call_logs_debug(self, gaming, caplog, tmp_path):
        import cv2
        import numpy as np
        p = str(tmp_path / "btn.png")
        cv2.imwrite(p, np.zeros((20, 20), np.uint8))
        gaming.findImageCenterLocations = lambda img, per=0.8, cutPoints=None, grayScreenshot=None: [(5, 5)]
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        with caplog.at_level(logging.DEBUG, logger="mcp-test"):
            server._do_click(p)
        msgs = [r.message for r in caplog.records]
        assert any("MCP 工具调用 [click] target=" in m for m in msgs)
        assert any("MCP 工具调用 [click] 完成 -> 已点击目标" in m for m in msgs)

    def test_screenshot_logs_byte_count(self, gaming, caplog):
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        with caplog.at_level(logging.DEBUG, logger="mcp-test"):
            server._do_screenshot()
        assert any("MCP 工具调用 [screenshot] 完成 -> " in r.message for r in caplog.records)

    def test_get_resolution_logs_debug(self, gaming, caplog):
        gaming.size = (2400, 1080)
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        with caplog.at_level(logging.DEBUG, logger="mcp-test"):
            server._do_get_resolution()
        msgs = [r.message for r in caplog.records]
        assert any("MCP 工具调用 [get_resolution]" in m for m in msgs)
        assert any("完成 -> 2400x1080" in m for m in msgs)

    def test_crop_screenshot_logs_debug(self, gaming, caplog):
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        with caplog.at_level(logging.DEBUG, logger="mcp-test"):
            server._do_crop_screenshot(1, 1, 5, 5)
        msgs = [r.message for r in caplog.records]
        assert any("MCP 工具调用 [crop_screenshot] (1,1) -> (5,5)" in m for m in msgs)
        assert any("完成 -> " in m for m in msgs)

    def test_save_screenshot_logs_debug(self, gaming, tmp_path, caplog):
        server = JczxMcpServer(make_save_host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        with caplog.at_level(logging.DEBUG, logger="mcp-test"):
            server._do_save_screenshot("d1")
        assert any("MCP 工具调用 [save_screenshot]" in r.message for r in caplog.records)

    def test_get_screenshot_mode_logs_debug(self, gaming, caplog):
        host = SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"),
                               config=SimpleNamespace(get_config=lambda opt: "annotated"))
        server = JczxMcpServer(host, 8765, logging.getLogger("mcp-test"))
        with caplog.at_level(logging.DEBUG, logger="mcp-test"):
            server._do_get_screenshot_mode()
        assert any("MCP 工具调用 [get_screenshot_mode]" in r.message for r in caplog.records)


class TestSaveScreenshot:
    """save_screenshot：保存到 template/{name}.png（与截图任务路径一致），可选裁切区域。"""

    def test_save_full_screenshot(self, gaming, tmp_path):
        import cv2
        server = JczxMcpServer(make_save_host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        result = server._do_save_screenshot("shot1")
        assert "截图已保存到" in result
        p = str(tmp_path / "template" / "shot1.png")
        assert os.path.exists(p), f"应保存到 {p}"
        img = cv2.imread(p)
        assert img.shape == (200, 200, 3)  # _SCREEN 尺寸

    def test_save_cropped_screenshot(self, gaming, tmp_path):
        import cv2
        import numpy as np
        gaming.screenshot = lambda: np.arange(20 * 20 * 3, dtype=np.uint8).reshape(20, 20, 3)
        server = JczxMcpServer(make_save_host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        server._do_save_screenshot("crop1", 5, 5, 10, 10)
        p = str(tmp_path / "template" / "crop1.png")
        assert os.path.exists(p)
        img = cv2.imread(p)
        assert img.shape == (5, 5, 3), f"应保存 5x5 裁切，实际 {img.shape}"

    def test_save_screenshot_invalid_crop_raises(self, gaming, tmp_path):
        server = JczxMcpServer(make_save_host(gaming, tmp_path), 8765, logging.getLogger("mcp-test"))
        try:
            server._do_save_screenshot("bad", 10, 10, 5, 5)
            assert False, "应抛裁切区域无效"
        except RuntimeError as e:
            assert "裁切区域无效" in str(e)


class TestGetScreenshotMode:
    """get_screenshot_mode：读取 TUI 的 debug.screenshot.mode，无配置回退 off。"""

    def test_returns_config_mode(self, gaming):
        host = SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"),
                               config=SimpleNamespace(get_config=lambda opt: "annotated"))
        server = JczxMcpServer(host, 8765, logging.getLogger("mcp-test"))
        assert server._do_get_screenshot_mode() == "annotated"

    def test_defaults_off_when_no_config(self, gaming):
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        assert server._do_get_screenshot_mode() == "off"


class TestRunEntity:
    """run_entity：按 section 名称依次执行实体。"""

    def test_executes_each_name_in_order(self, gaming):
        executed = []
        gaming.exec = lambda name: executed.append(name)
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        result = server._do_run_entity("task-a", "click-b")
        assert executed == ["task-a", "click-b"], "应按参数顺序依次执行"
        assert result == "已执行实体: task-a, click-b"

    def test_invalid_name_raises(self, gaming):
        executed = []
        gaming.exec = lambda name: executed.append(name)
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        try:
            server._do_run_entity("ok", None)
            assert False, "应抛实体名称无效"
        except RuntimeError as e:
            assert "实体名称无效" in str(e)
        assert executed == ["ok"], "无效名称前的实体应已执行"

    def test_run_entity_logs_debug(self, gaming, caplog):
        gaming.exec = lambda name: None
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        with caplog.at_level(logging.DEBUG, logger="mcp-test"):
            server._do_run_entity("click-a")
        assert any("MCP 工具调用 [run_entity]" in r.message for r in caplog.records)
        assert any("MCP 执行实体 [click-a]" in r.message for r in caplog.records)


class TestRunEntityJson:
    """run_entity_json：入参 JSON 串，方法内构建 JczxSectionEntity 后执行。"""

    def test_parses_json_and_builds_entity(self, gaming):
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        # func: context_set 会被引擎解析并在 _context 里写入变量，可验证实体真正被构建执行
        result = server._do_run_entity_json(
            '{"type": "func", "func": "context_set", "args": "json_key,jason_val"}'
        )
        assert "已执行 JSON 实体 type=func" in result
        assert gaming._context.get("json_key") == "jason_val", "实体应被真实执行并写入上下文"

    def test_invalid_json_raises(self, gaming):
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        try:
            server._do_run_entity_json("{not valid")
            assert False, "应抛 JSON 解析失败"
        except RuntimeError as e:
            assert "JSON 解析失败" in str(e)

    def test_missing_type_raises(self, gaming):
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        try:
            server._do_run_entity_json('{"target": "buttons/login.png"}')
            assert False, "应抛缺少 type 字段"
        except RuntimeError as e:
            assert "必须是含 type 字段" in str(e)

    def test_non_object_raises(self, gaming):
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        try:
            server._do_run_entity_json('["a", "b"]')
            assert False, "应抛非对象"
        except RuntimeError as e:
            assert "必须是含 type 字段" in str(e)

    def test_empty_or_non_string_raises(self, gaming):
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        for bad in ("", None, 123):
            try:
                server._do_run_entity_json(bad)
                assert False, f"应抛无效入参: {bad!r}"
            except RuntimeError as e:
                assert "JSON 入参无效" in str(e)

    def test_click_entity_clicked_center(self, gaming, tmp_path):
        import json
        import cv2
        import numpy as np
        p = str(tmp_path / "btn.png")
        cv2.imwrite(p, np.zeros((20, 20), np.uint8))
        gaming.findImageCenterLocations = lambda img, per=0.8, cutPoints=None, grayScreenshot=None: [(30, 40)]
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        # 用 json.dumps 保证 Windows 反斜杠路径被正确转义为合法 JSON
        json_str = json.dumps({"type": "click", "target": p, "max_wait": 10})
        result = server._do_run_entity_json(json_str)
        assert "type=click" in result
        assert gaming.clicks == [(30, 40)], "click 实体应点击匹配中心"

    def test_run_entity_json_logs_debug(self, gaming, caplog):
        server = JczxMcpServer(make_host(gaming), 8765, logging.getLogger("mcp-test"))
        with caplog.at_level(logging.DEBUG, logger="mcp-test"):
            server._do_run_entity_json(
                '{"type": "func", "func": "context_set", "args": "k,v"}'
            )
        assert any("MCP 工具调用 [run_entity_json]" in r.message for r in caplog.records)
        assert any("MCP 执行 JSON 实体" in r.message for r in caplog.records)


class TestWriteConfig:
    """write_config：复用 TxtConfig.set_config+save() 写任务文件，校验同名冲突与逗号空格。"""

    def _host(self, gaming, tmp_path):
        cfg_dir = tmp_path / "Config"
        return SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"),
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


class TestRegisterFile:
    """register_file：在 MainMenu 写入 type:file 注册，重复 key 报错。"""

    def _host(self, gaming, tmp_path):
        from jczx.CommonBuilder.CommonBuilder.FileTools.ConfigUtils import TxtConfig
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

    def test_registers_without_polluting_merged_externals(self, gaming, tmp_path):
        """内存 menu_config 已 merge 外部 task 文件段时，register_file 不得把外部段写回 MainMenu（防污染）。

        回归锁定：_do_register_file 用磁盘干净实例写入，避免直接 save() 把外部段序列化进 MainMenu.txt。
        """
        from jczx.CommonBuilder.CommonBuilder.FileTools.ConfigUtils import TxtConfig
        cfg_dir = tmp_path / "Config"
        menu_path = cfg_dir / "MainMenu.txt"
        os.makedirs(cfg_dir, exist_ok=True)
        # 磁盘上的 MainMenu 是干净的
        disk_mm = TxtConfig(str(menu_path))
        disk_mm.set_config("goto-home", "type", "task"); disk_mm.save()
        # 内存 menu_config 模拟运行时已 merge 外部段（如 jjc-thumb）
        mm = TxtConfig(str(menu_path))
        ext_path = cfg_dir / "tasks" / "jjc.txt"
        os.makedirs(ext_path.parent, exist_ok=True)
        ext = TxtConfig(str(ext_path))
        ext.set_config("jjc-thumb", "type", "click"); ext.save()
        mm.merge(ext)
        tm = SimpleNamespace(menu_config=mm, menu_config_path=str(menu_path), config_dir=str(cfg_dir))
        host = SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"),
                               fm=FakeFm(str(tmp_path)), task_manage=tm)
        server = JczxMcpServer(host, 8765, logging.getLogger("mcp-test"))
        server._do_register_file("file-record-a", "tasks\\record_a.txt", "记录A")
        # 从磁盘重新读，断言：不含外部段 jjc-thumb，只含本 key 与 goto-home
        reloaded = TxtConfig(str(menu_path))
        assert "jjc-thumb" not in reloaded.sections(), "register_file 不得把已 merge 的外部段写回 MainMenu"
        assert reloaded.get_config("file-record-a", "type") == "file"
        assert reloaded.get_config("file-record-a", "target") == "tasks\\record_a.txt"
        assert reloaded.get_config("file-record-a", "name") == "记录A"


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


class TestReadLogTail:
    """read_log_tail：读取日志文件最后 N 行（host 提供 log_file 时用之）。"""

    def _make_log_server(self, gaming, tmp_path, lines):
        p = tmp_path / "JczxTUI.log"
        p.write_text("\n".join(lines), encoding="utf-8")
        host = SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"),
                               log_file=str(p))
        return JczxMcpServer(host, 8765, logging.getLogger("mcp-test"))

    def test_returns_last_n_lines(self, gaming, tmp_path):
        server = self._make_log_server(gaming, tmp_path,
                                       ["line1", "line2", "line3", "line4", "line5"])
        result = server._do_read_log_tail(2)
        assert result == "line4\nline5", "应返回最后 2 行"

    def test_returns_all_when_n_ge_length(self, gaming, tmp_path):
        server = self._make_log_server(gaming, tmp_path, ["a", "b"])
        assert server._do_read_log_tail(100) == "a\nb"

    def test_resolves_default_path_by_class_name(self, gaming, tmp_path):
        log = tmp_path / "JczxTUI.log"
        log.write_text("hello-log", encoding="utf-8")

        class FakeTuiHost:
            # 模拟 JczxTUI 实例：__name__ 固定为 JczxTUI，_program_dir 指向 tmp
            device = gaming
            logger = logging.getLogger("mcp-test")

            @staticmethod
            def _program_dir():
                return str(tmp_path)

        host = FakeTuiHost()
        # __name__ 取的是类名 JczxTUI（此处类名是 FakeTuiHost），需手动覆盖供工具识别
        host.__class__ = type("JczxTUI", (FakeTuiHost,), {})
        server = JczxMcpServer(host, 8765, logging.getLogger("mcp-test"))
        assert server._do_read_log_tail(10) == "hello-log"

    def test_invalid_lines_raises(self, gaming, tmp_path):
        server = self._make_log_server(gaming, tmp_path, ["x"])
        for bad in (0, -5, 3.5, "10"):
            try:
                server._do_read_log_tail(bad)
                assert False, f"应抛非法 lines: {bad!r}"
            except RuntimeError as e:
                assert "必须为正整数" in str(e)

    def test_missing_file_raises(self, gaming):
        host = SimpleNamespace(device=gaming, logger=logging.getLogger("mcp-test"),
                               log_file="/no/such/file.log")
        server = JczxMcpServer(host, 8765, logging.getLogger("mcp-test"))
        try:
            server._do_read_log_tail(5)
            assert False, "应抛日志文件不存在"
        except RuntimeError as e:
            assert "日志文件不存在" in str(e)

    def test_read_log_tail_logs_debug(self, gaming, tmp_path, caplog):
        server = self._make_log_server(gaming, tmp_path, ["m1", "m2", "m3"])
        with caplog.at_level(logging.DEBUG, logger="mcp-test"):
            server._do_read_log_tail(2)
        assert any("MCP 工具调用 [read_log_tail]" in r.message for r in caplog.records)
        assert any("完成 -> 2 行" in r.message for r in caplog.records)


class TestInitMcp:
    def test_init_mcp_starts_daemon_thread(self, monkeypatch):
        cli = object.__new__(JczxCli)
        cli.config = SimpleNamespace(get_config=lambda opt: "8765")
        cli.logger = logging.getLogger("mcp-init-test")
        started = []

        class FakeThread:
            def __init__(self, target, daemon=False, name=None):
                self.target, self.daemon, self.name = target, daemon, name

            def start(self):
                started.append(self)

        monkeypatch.setattr("jczx.jczxCli.threading.Thread", FakeThread)
        monkeypatch.setattr("jczx.mcpServer.JczxMcpServer",
                            lambda host, port, logger: SimpleNamespace(host=host, port=port, run=lambda: None))
        cli._init_mcp()
        assert len(started) == 1
        assert started[0].daemon is True
        assert started[0].name == "jczx-mcp"
        assert cli._mcp_server.port == 8765

    def test_init_mcp_port_fallback(self, monkeypatch):
        cli = object.__new__(JczxCli)
        cli.config = SimpleNamespace(get_config=lambda opt: "abc")  # 非法端口
        cli.logger = logging.getLogger("mcp-init-test")
        monkeypatch.setattr("jczx.jczxCli.threading.Thread",
                            lambda target, daemon, name: SimpleNamespace(start=lambda: None))
        monkeypatch.setattr("jczx.mcpServer.JczxMcpServer",
                            lambda host, port, logger: SimpleNamespace(host=host, port=port))
        cli._init_mcp()
        assert cli._mcp_server.port == 8765

    def test_init_mcp_port_fallback_missing_key(self, monkeypatch):
        """Config.txt 缺 mcp.port 键（get_config 抛 KeyError）时应回退默认 8765。"""
        cli = object.__new__(JczxCli)
        cli.config = SimpleNamespace(get_config=lambda opt: (_ for _ in ()).throw(KeyError(opt)))
        cli.logger = logging.getLogger("mcp-init-test")
        monkeypatch.setattr("jczx.jczxCli.threading.Thread",
                            lambda target, daemon, name: SimpleNamespace(start=lambda: None))
        monkeypatch.setattr("jczx.mcpServer.JczxMcpServer",
                            lambda host, port, logger: SimpleNamespace(host=host, port=port))
        cli._init_mcp()
        assert cli._mcp_server.port == 8765

    def test_init_mcp_failure_logs_error(self, monkeypatch, caplog):
        cli = object.__new__(JczxCli)
        cli.config = SimpleNamespace(get_config=lambda opt: "8765")
        cli.logger = logging.getLogger("mcp-init-test")

        def boom(host, port, logger):
            raise RuntimeError("端口占用")

        monkeypatch.setattr("jczx.mcpServer.JczxMcpServer", boom)
        with caplog.at_level(logging.ERROR, logger="mcp-init-test"):
            cli._init_mcp()
        assert any("MCP 服务启动失败" in r.message for r in caplog.records)

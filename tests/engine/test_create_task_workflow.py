"""组装级：save_template→write_config→register_file→reload_config→run_entity 闭环。"""
import logging
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
    # make_gaming 需要 real_config_dir 位置参数；用只读副本目录构造 task_manage
    gaming = make_gaming(str(real_config_copy))
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

# 交错战线 AutoScript

交错战线手游自动化脚本，基于 ADB + cv2 模板匹配 + PaddleOCR。Windows，Python >=3.14。

本项目使用 [uv](https://docs.astral.sh/uv/) 管理 Python 环境与依赖（`uv.lock` 锁定版本）。

## 快速开始

```powershell
# ① 安装/同步依赖（含 dev 依赖组，自动创建 .venv）
uv sync

# ② 激活虚拟环境（可选，uv run 不需要激活）
.\.venv\Scripts\activate

# ③ 运行 Textual TUI（主入口）
uv run python -m jczx.jczxCli
# 或激活后直接：
python -m jczx.jczxCli

# 构建可执行文件（交互式选择 pyinstaller 或 nuitka）
python build.py
```

> **环境说明**：项目是 uv 管理环境，`uv sync` 会按 `pyproject.toml` 同步 `dependencies` 与 `[dependency-groups] dev`（pytest 等），并生成/复用 `.venv`。日常运行直接用 `uv run python -m jczx.jczxCli`，无需手动激活。

## 功能

| 功能 | 说明 |
|------|------|
| 检测式启动游戏 | 自动启动游戏 App，首次启动自动签到 |
| 自动交付订单 | 自定义订单类型，支持自动合成 |
| 周本虚影微晶 | 阿瑞斯/宙斯虚影，支持预设队伍 |
| 虚影刷好感 | 自定义队伍和次数 |
| 竞技场挑战 | OCR 战力识别，可设置战力阈值 |
| 矿场配队计算 | 计算配队方案得分 |
| 驻员预设切换 | 工作成员心情耗尽时自动切换到心情正常的预设（method+call+index 逐设施） |

## 架构

| 入口 | 命令 |
|------|------|
| TUI（推荐） | `python -m jczx.jczxCli` |
| GUI（旧版） | `python jczx/jczx.py` |

旧版 PyQt6 GUI 已不再维护，推荐使用新版 Textual TUI。

## 模拟器推荐

雷电模拟器，开启 ADB 本地调试。MuMu 需开桥接模式。

已测试分辨率：1920×1080 (dpi 280)、2400×1080 (dpi 320)。

## 构造软链接（从仓库根目录运行时）

```
mklink /J resources jczx\resources
```

## 配置文件

| 文件 | 用途 |
|------|------|
| `jczx/Config/Config.txt` | 全局设置（日志、线程、ADB 路径、调试截图模式、`mcp.port`） |
| `jczx/Config/MainMenu.txt` | 公共实体 + 任务入口（支持 `type: file` 引入子文件） |
| `jczx/Config/Queues.txt` | 任务队列定义（顺序执行多个任务） |
| `jczx/Config/tasks/*.txt` | 各模块任务（jjc、inllusion、Favor、Construction、staff_switch_auto 等），经 `type: file` 合并 |
| `jczx/Config/common_entities.md` | 通用实体速查（goto-home、click-center、wait-1 等） |
| `TASK_CONFIG_GUIDE.md` | 任务配置完整文档（权威，改任务前必读） |

## TUI 功能

| 功能 | 说明 |
|------|------|
| 任务列表 + 启停 | 左侧任务卡片，勾选启动/停止 |
| 任务设置 | 右侧设置面板，动态表单 |
| 任务队列 | 创建/编辑/删除队列，顺序执行，拖拽排序，与单任务互斥 |
| 调试截图 | 两种模式：连续截图（simple）/ 标注截图（annotated），配置控制 |
| 记录窗口 | 录制手动操作，产出 `record_*.json` + 标注截图，可转成任务配置 |

## MCP 服务（agent 可控制设备）

TUI 启动时会异步加载内嵌 MCP 服务（streamable-http），暴露设备/配置工具，供 Claude Code 等 agent 连接操作。**需 TUI 运行且设备已连接。**

- 端口：`Config.txt` 的 `mcp.port`（默认 `8765`）
- 连接方式：`http://127.0.0.1:8765/mcp`

内置工具：`screenshot` / `click` / `swipe` / `drag` / `get_resolution` / `crop_screenshot` / `save_screenshot` / `save_template` / `get_screenshot_mode` / `run_entity` / `run_entity_json` / `reload_config` / `write_config` / `register_file` / `list_templates` / `read_log_tail`。

agent 侧（`.mcp.json`）已配好：

```json
{
  "mcpServers": {
    "jczx-tui": {
      "type": "http",
      "url": "http://127.0.0.1:8765/mcp"
    }
  }
}
```

## 生成任务配置（skill）

项目在 `.claude/skills/` 提供辅助技能：

| Skill | 用途 |
|-------|------|
| `tui-config` | 配置语法权威（点击/匹配/OCR/条件/上下文/多文件/method-call/设置/示例） |
| `create-task-from-record` | 辅助用户把记录模式产出转成任务配置（模板由用户提供，只用不裁；复杂场景硬门禁） |

## 单元测试

```powershell
uv run pytest                # 全部
uv run pytest tests/pure     # 纯逻辑单测
uv run pytest tests/engine   # 引擎级测试（FakeDevice 桩替身，不连 ADB）
uv run pytest tests/regression  # 真实配置只读副本回归
```

新增特性必须配套单元测试（`tests/pure` / `tests/engine` / `tests/regression`）。

## 调试截图

`jczx/Config/Config.txt` 中设置 `debug.screenshot.mode`：
- `off` — 关闭
- `simple` — 每次截图保存至 `screenHistory/N.png`
- `annotated` — 标注匹配/点击/滑动/OCR 位置后保存

合成视频（需安装 ffmpeg）：

```powershell
# PNG 序列 → MP4（10 fps）
ffmpeg -framerate 10 -i screenHistory/%d.png -c:v libx264 -pix_fmt yuv420p output.mp4

# 指定起始序号
ffmpeg -start_number 1 -framerate 10 -i screenHistory/%d.png -c:v libx264 -pix_fmt yuv420p output.mp4
```

## 快捷键

| 按键 | 功能 |
|------|------|
| `q` | 退出程序 |
| `ctrl+l` | 清空日志控制台 |
| `ctrl+shift+c` | 复制全部日志到剪贴板 |

## 依赖

依赖由 `pyproject.toml` 管理，`uv sync` 自动安装。核心依赖：

```
opencv-python>=4.13
onnxruntime>=1.26
paddleocr>=3.7
textual>=8.2
uiautomator2>=3.5
requests>=2.34
mcp[cli]>=2.0
```

## 构建

```powershell
python build.py
```

交互式选择 `pyinstaller`（快，包大）或 `nuitka`（慢，包小）。

# 第 9 章 可用 func 方法

`func` 类型实体调用引擎上的方法。`func` 字段填方法名，`target`/`args` 作为参数（`target` 是首参数，与 `args` 合并）。

方法分派逻辑（`jczxCli.py` 的 `_get_method`）：`method_name in self.__dir__()` 则调用。由于 `JCZXGaming` 继承 `Device`，可调用的方法包含引擎自定义方法 + ADB/Device 基类方法。

## 9.1 func 调用方式

```ini
[in_location]
type: func
func: in_location
target: buttons\fight.png
args: 0.95
```

引擎 `exec_func` 组装参数：`raw_args = ([e.target] if e.target else []) + e.args`，再按顺序传给方法。因此第一个实参来自 `target`，其余来自 `args`。

## 9.2 引擎自定义方法（JCZXGaming）

| 方法 | 签名 | 说明 |
|------|------|------|
| `in_location` | `(target, per=0.8)` | 检测图片是否在当前屏幕可见，返回 bool |
| `near_location` | `(target, match_key, per=0.8)` | 在 match 实体的匹配区域内搜索 target 图片，找到返回 True |
| `start_game` | `(app, activity)` | 若 app 未运行则启动 activity |
| `launch_emulator` | `(index="0")` | 启动模拟器 |
| `shutdown_emulator` | `(index="0")` | 关闭模拟器 |
| `save_screenshot` | `(dir, name)` | 保存截图到 `dir/name.png` |
| `click_proportion` | `(w_pro, h_pro)` | 按屏幕比例点击（`w=2,h=2` 即中点） |
| `drag_drop_proportion` | `(w1,h1,w2,h2,duration=200)` | 按屏幕比例拖拽 |
| `swipe_proportion` | `(w1,h1,w2,h2,duration=200)` | 按屏幕比例滑动 |
| `string_concat` | `(*args)` | 字符串拼接 |
| `context_get` | `(key, default="")` | 读上下文变量 |
| `context_set` | `(key, value)` | 写上下文变量 |
| `context_print` | `()` | 打印全部上下文变量（调试） |
| `parse_placeholder` | `(key)` | 解析占位符 |

## 9.3 常用基础方法（Device/Adb 基类）

这些是继承自 `Device` 的通用方法，常用于 `func`：

| 方法 | 签名 | 说明 |
|------|------|------|
| `get_app_pid` | `(package_name)` | 返回进程 PID（未运行返回假值） |
| `get_app_activity` | `(package_name)` | 返回前台 activity |
| `launch_app` | `(activity)` | 启动 activity |
| `kill_app` | `(package_name)` | 杀应用 |
| `click` | `(x, y)` | 点击坐标 |
| `swipe` | `(x1,y1,x2,y2,duration=200)` | 滑动 |
| `dragAndDrop` | `(x1,y1,x2,y2,duration=200)` | 拖拽 |
| `getScreenSize` | `()` | 返回 `(width, height)` |

## 9.4 示例

```ini
/ 判断主界面（返回 bool 存上下文）
[condition-in_location-home]
type: func
func: in_location
target: buttons\fight.png
args: 0.95

/ 按比例点击屏幕中点
[click-center]
type: func
func: click_proportion
args: 2,2

/ 保存截图
[screenshot]
type: func
func: save_screenshot
args: template,${screenshot-task-values:screenshot-name}

/ 启动游戏
[launch-game-plan]
type: func
func: start_game
args: com.megagame.crosscore,com.megagame.crosscore/com.mjsdk.app.MJUnityActivity
```

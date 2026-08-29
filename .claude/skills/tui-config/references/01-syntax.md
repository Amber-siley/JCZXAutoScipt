# 第 1 章 语法与类型总览

## 1.1 配置文件

| 文件 | 路径 | 用途 |
|------|------|------|
| 主配置 | `jczx/Config/Config.txt` | 日志、线程、ADB 路径等全局设置 |
| 任务配置 | `jczx/Config/MainMenu.txt` | 公共实体 + 子文件入口引用 |
| 子配置文件 | `jczx/Config/tasks/*.txt` | 各模块任务定义（通过 `type: file` 引入） |
| 队列 | `jczx/Config/Queues.txt` | 任务队列（`[queue-xxx]` 内 `tasks:` 列表，顺序执行） |

任务较多时建议拆分子文件，MainMenu.txt 仅保留公共实体和 `type: file` 声明。

## 1.2 语法

```ini
/            ← 注释（/ 或 // 开头）
[section]    ← 节名，该实体的唯一标识 key
key : value  ← 键值对，冒号分隔，不是 =
```

- 逗号分隔的字符串自动解析为列表（在 `BaseEntity.__setattr__` 中按 `,` 拆分并转类型）。
- **关键：逗号后不要加空格**。`action: a,b,c` 正确；`action: a, b, c` 会产生 `" b"`、`" c"`——带前导空格，实体 lookup 失败。
- 值若含 `${}` / `@{}` / `%{}` 占位符，会被保留为原始字符串延迟解析，不做类型转换。

## 1.3 实体类型总览

每个 `[key]` 都是一节实体，`type` 决定引擎怎么执行它。

| 类型 | 说明 | action 链 | 说明 |
|------|------|-----------|------|
| `task` | 通用过程入口，view=on 时为 TUI 任务，view=off 时为幕后过程 | ✓ | `action` = 子实体链 |
| `func` | 调用 `JCZXGaming` 方法 | ✓ | `func` 指定方法名 |
| `click` | 模板匹配 + 点击 | ✓ | 支持 pos / match / target 三种模式 |
| `dynamic` | 动态执行 | ✗ | `action` = 循环源；返回值作为新 key 二次执行 |
| `match` | 纯匹配，返回坐标 | ✗ | `action` = 坐标变换操作 |
| `ocr` | 匹配 + 裁剪 + OCR | ✓ | 返回识别文本 |
| `context` | 上下文变量运算 | ✗ | `action` = 运算链 |
| `condition` | 条件分支控制 | ✓ | 评估 `condition`/`condition_not` |
| `settings` | 设置容器 | — | 引用 `setting` 字段 |
| `setting` | 设置字段定义 | — | 描述表单控件 |
| `file` | 外部配置文件引用 | — | 加载子配置文件中的实体合并到同一 `entity_pool` |
| `method` | 可复用、带参数的执行链 | ✓ | `params`/`param_defaults` 声明参数，`action` = body |
| `call` | 调用 method，参数绑定进 context | ✓ | `fn` = 目标 method，`args` = 位置参数 / kwargs |

**三种特殊 action 语义**（与普通执行链不同，尤其注意）：

- `match` 的 `action` = **坐标变换操作**（`down|1.5`、`reW|2.0`、`right-M|30` 等）
- `context` 的 `action` = **数值/字符串运算链**（`+|1`、`x|2`、`contains|关键词`）
- `dynamic` 的 `action` = **循环源**（每个元素执行后，返回值作为新 key 再次 exec）

别把这三者的 `action` 当成普通执行链来写。

## 1.4 字段分类

字段定义见 `jczx/configEntity.py` 的 `JczxSectionEntity`。分为几组：

- **通用**：`type` / `name` / `desc` / `action` / `times` / `view` / `pre_sleep` / `sleep` / `log` / `log_level` / `max_wait` / `screen_cache_ttl` / `context_key` / `context_type` / `context_default_type` / `extend` / `only_key`(系统赋值) / `queueable`
- **门控与等待**：`testFor_before` / `testFor_after` / `testFor_max_wait` / `testFor_per` / `testFor_pre_sleep` / `testFor_sleep` / `wait_target` / `wait_target_per` / `wait_target_sleep`
- **条件**：`condition` / `condition_not` / `condition_then` / `condition_else`
- **method/call**：`fn` / `params` / `param_defaults`
- **context**：`context_get` / `context_default` / `context_default_type` / `values`

### 通用字段选摘

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `type` | str | — | **必填** |
| `name` | str | — | 显示名称（中文） |
| `desc` | str | — | 长文本备注 |
| `action` | list[str] | `[]` | 执行后链式调用的实体 key 列表（三类特殊语义见上） |
| `times` | int | `1` | 执行次数 |
| `view` | str | `off` | `on`= TUI 中显示为任务（日志 info）；`off`= 幕后过程（日志 debug） |
| `context_key` | str | — | 返回值存入上下文变量的 key |
| `context_type` | str | `str` | 存储前的类型转换：`str`/`int`/`float`/`bool` |
| `pre_sleep` | float | `0` | 执行前等待秒数 |
| `sleep` | float | `0` | 自身逻辑完成后、action 链前的等待秒数 |
| `extend` | str | — | 继承另一实体的字段（须同文件） |
| `max_wait` | float | `0` | wait_target / click 最大等待秒数。`0` 表示不等待 |
| `log` | str | — | 自定义日志消息，支持四种占位符 |
| `log_level` | str | `info` | log 等级：`debug`/`info`/`warning`/`error` |
| `screen_cache_ttl` | float | `-1` | 截图缓存 TTL（毫秒）。`-1`=继承上级，`0`=禁用，`N`=自定义 |

## 1.5 命名约定

- key 用 `类型-动作` 英文风格：`click-fight`、`condition-to-home`、`match-Daily`。
- `name` / `desc` 用中文，作为 TUI 显示名。
- 跨任务复用的公共实体（`in_location`、`click-center`、`goto-home`、`auto-fight`）留在 MainMenu。

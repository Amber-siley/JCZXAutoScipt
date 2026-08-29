# 第 7 章 任务设置表单

TUI 界面里可以让用户调整任务参数。三个层级：**task → settings 容器 → setting 字段**。

## 7.1 结构

```ini
[order-delivery]
type: task
settings: order-delivery-settings

[order-delivery-settings]
type: settings
fields: enable-orders, enable-craft

[enable-orders]
type: setting
setting_type: multi_select
label: 启用订单
options: 初级订单,中级订单,高级订单,特殊订单
```

## 7.2 支持的控件类型

| setting_type | TUI 控件 | 值格式 |
|-------------|---------|--------|
| `input` | 文本输入框 | 自由文本 |
| `integer` | 数字输入框（min/max） | 整数字符串 |
| `select` | 下拉选择框 | 单个选项值 |
| `multi_select` | 多选框 | 逗号分隔选中项 |
| `multi_select_switch` | 主开关 + 子开关 | 选中项，子开关另存 `{name}__sub` |
| `bool` | 单开关 `[X] 标签` | `true` / `false` |

值存储到 `{task-key}-values` section，读取时优先取值、其次 `default`。

## 7.3 bool 使用示例

缺省用 `default`，用户设置后存 `{task-key}-values`。

```ini
[delivery-settings]
type: settings
fields: enable-delivery, enable-synth

[enable-delivery]
type: setting
setting_type: bool
label: 是否交付
default: true

[enable-synth]
type: setting
setting_type: bool
label: 是否按需合成
default: false
```

- 开关关时保存 `false`，开时保存 `true`。
- 执行链中用 `${delivery-values:enable-delivery}` 读取；引擎 `_convert_value` 将 `true`/`1`/`yes` 判定为真，可配合 `context_type: bool` 或 `&{...}` 条件使用。
- 单行渲染为 `[X] 标签`，与 `multi_select_switch` 的行内开关样式一致。

## 7.4 读取设置值

在任务 action 链里用 `${task-key-values:field-name}` 读取（task-key 是引用 settings 的 task 实体 key）：

```ini
[launch_emulator_task]
extend: launch_emulator
args: ${emu-values:emu-setting-index}

[emu-settings]
type: settings
fields: emu-manager-path,emu-setting-index

[emu-setting-index]
type: setting
setting_type: integer
label: 模拟器索引

[emu-values]
emu-setting-index: 0
emu-manager-path: D:\Software\MuMu\MuMuPlayer\nx_main\MuMuManager.exe
```

注意 `{task-key}-values` section 也直接在配置文件里定义，提供默认值。

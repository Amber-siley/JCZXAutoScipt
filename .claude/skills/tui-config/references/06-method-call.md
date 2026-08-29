# 第 6 章 method / call

`method` 定义可复用的参数化执行链，`call` 调用它并把参数绑定进 context（函数体内用 `%{param}` 读取）。适合把一段带差异点的流程抽取成模板。

## 6.1 method 定义

| 字段 | 说明 |
|------|------|
| `params` | 声明参数名（逗号分隔），用于校验与位置绑定 |
| `param_defaults` | 可选参数默认值（`k=v` 逗号分隔） |
| `action` | **body**，执行链 |

```txt
/ ===== method 定义 =====
[if-next-to-click]
type: method
name: 若基础图旁出现邻居图则点击
params: base, neighbor, neighbor_match
action: near-check, cond-click

[near-check]
type: func
func: near_location
args: %{neighbor}, %{neighbor_match}
context_key: near_ok

[cond-click]
type: condition
condition: %{near_ok}
condition_then: click-target

[click-target]
type: click
target: %{base}
```

## 6.2 call 调用

| 字段 | 说明 |
|------|------|
| `fn` | 目标 method 实体 key |
| `args` | 位置参数 / kwargs |

```txt
/ ===== call 调用（位置参数）=====
[call-exploration]
type: call
fn: if-next-to-click
args: buttons\ExplorationGuidelines.png, locations\hasNew.png, match-exploration-to-new

[task-receive-x]
type: task
action: goto-home, call-exploration, goto-home
```

## 6.3 要点

- **位置参数**：`args` 中无 `=` 的值按 method `params` 声明顺序绑定；**kwargs**：`key=value` 按名绑定；两者可混用，显式值覆盖 `param_defaults` 默认值。
- 参数绑定进**全局 context**，调用后保留（不自动恢复），函数体内实体用 `%{param}` 读取。
- 校验：缺少必填参数 / 多余参数 / 位置参数超出 / 目标不是 method → `log.warning`（不中断执行）。
- **嵌套调用**：method body 的 `action` 里可再写 `call` 实体；内层 call 的参数值支持 `%{}` 引用外层参数（绑定前解析）。
- `method` / `call` 不进任务列表与队列（`view`/`queueable` 对其无效）。
- `args`/`values` 的值**不能含逗号**（与现有规则一致）。

## 6.4 完整示例（参考 receive.txt）

```ini
/ ===== method：若基础图周围出现邻居图则点击 =====
[if-around-click]
type: method
name: 若基础图周围出现邻居图则点击
params: base,base_per,neighbor,then_entity,expand_up,expand_down,expand_left,expand_right,click_sleep
param_defaults: neighbor=locations\hasNew.png,base_per=0.8,then_entity=click-target,expand_up=40,expand_down=40,expand_left=40,expand_right=40,click_sleep=1
action: matched-around,cond-click

[matched-around]
type: match
match: match-around
target: %{neighbor}
context_key: near_ok
context_type: bool

[match-around]
type: match
target: %{base}
per: %{base_per}
action: up-M|%{expand_up},down-M|%{expand_down},left-M|%{expand_left},right-M|%{expand_right}

[cond-click]
type: condition
condition: &{%{near_ok}}
condition_then: %{then_entity}

[click-target]
type: click
target: %{base}
per: %{base_per}
sleep: %{click_sleep}

/ ===== call：勘探指南周围有 hasNew 则点击 =====
[call-exploration-around]
type: call
fn: if-around-click
args: base=buttons\ExplorationGuidelines.png,then_entity=click-exploration
```

**`values` 批量初始化**（不触发 method，仅设变量）：

```ini
[init-params]
type: context
values: base=buttons\a.png, neighbor=locations\b.png
```

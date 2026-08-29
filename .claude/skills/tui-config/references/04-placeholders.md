# 第 4 章 占位符解析

四种占位符由统一的 `PlaceholderResolver` 引擎处理，单一入口 `resolve(text, after_key)` 按固定顺序解析。

## 4.1 总览对比

| 占位符 | 含义 | 解析方式 | 可用字段 | 解析顺序 |
|--------|------|---------|---------|---------|
| `${section:option}` | 配置值 | 从配置文件读取 | **所有字段** | ① |
| `@{entity_key}` | 实体返回值 | 执行实体，用返回值替换 | **所有字段** | ② |
| `%{context_key}` | 上下文变量 | 从 `_context` 读取 | **所有字段** | ③ |
| `&{表达式}` | 条件表达式 | 执行表达式内实体 + 逻辑/比较运算 | `condition`/`condition_not`、`log` | ④ |

三种字符串占位符（`${}` / `@{}` / `%{}`）作用域完全一致，覆盖 entity key、action 链、所有标量字段；`&{...}` 仅用于条件求值和 log 展示。

**架构说明**：所有解析通过 `PlaceholderResolver` 统一入口完成，保证 `${}` → `@{}` → `%{}` → `&{...}` 顺序。`condition` 字段通过 `evaluate_condition()` 求值（返回 `"True"`/`"False"`），同时支持 `&{...}` 表达式和裸实体 key。条件日志通过 `format_condition()` 展示解析后的表达式文本。

## 4.2 `${...}` — 配置占位符

从配置文件读取值。**作用于所有字段。**

| 形式 | 含义 | 示例 |
|------|------|------|
| `${section:option}` | 指定 section 下的 option | `${screenshot-values:name}` |
| `${section:option:default}` | 带默认值 | `${mine-values:level:5}` |
| `${option}` | 短格式 → `{当前实体.only_key}-values:{option}` | `${screenshot-name}` |

示例：

```ini
[screenshot]
type: func
func: save_screenshot
args: ${screenshot-task-values:dir},${screenshot-name}
```

## 4.3 `@{...}` — 执行占位符

运行一个实体，将其返回值替换到字符串中。**作用于所有字段**，包括 action 链中的 entity key。

```ini
[get-device]
type: func
func: get_app_activity
args: com.megagame.crosscore

[save-screenshot]
type: func
func: save_screenshot
args: @{get-device},${screenshot-name}
```

## 4.4 `%{...}` — 上下文占位符

读取 `context_set` / `context_key` 存入的变量（类型为 `str`/`int`/`float`/`bool`），同时支持表达式求值。**作用于所有字段。**

```ini
[use-power]
type: func
func: context_set
args: threshold_check,%{power_value}
```

**表达式模式**（含运算符如 `&`、`|`、`>=`、`<=`、`>`、`<`、`==`、`!=` 时自动识别）：

```ini
condition: &{combat_power >= 50000 & score > %{min_threshold}}
log: 剩余次数=%{total_times > refresh_times}
```

解析规则：`%{key > 5}` → 读取 `key` 上下文变量 → 与 `5` 比较 → 返回 `True`/`False`。表达式中也可混用 `${...}` `@{...}` `%{...}` 子占位符。

## 4.5 `&{...}` — 条件表达式

用于 `condition` / `condition_not` 字段和 `log` 字段，组合多实体和变量的返回值进行逻辑/比较运算。

```ini
condition: &{entity_a & (entity_b | entity_c >= 2)}
```

操作数与运算符见第 3 章 condition 部分。优先级（低→高）：`|` → `&` → `>=` `<=` `>` `<` `==` `!=` → `()`

**log 中的 &{...}**：嵌入式 `&{...}` 会被替换为最终布尔结果（`True`/`False`），不再保留中间表达式文本。

```ini
[complex-check]
type: click
target: buttons\buy.png
condition: &{can_buy & (get-buy-times > 3 | get-diamond >= ${shop:price})}
condition_then: do-purchase

/ 比较实体结果和上下文变量
condition: &{check-power & %{combat_power} >= 50000}
```

**条件日志格式**：满足/不满足时打印 `条件 &{原始表达式} → &{${}和%{}已替换} → 结果`，便于调试。

## 4.6 log 字段中的多占位符混用

`log` 字段唯一支持四种占位符同时使用：

```ini
[debug-task]
type: click
target: buttons\login.png
log: 战力=%{power}, 阈值=${arena:threshold}, 状态@{check}, 判断&{enable >= 1}
log_level: debug
```

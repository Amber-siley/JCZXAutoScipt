# 第 3 章 condition / context

两章关系：`condition` 做**分支控制**，`context` 做**状态变量记录与运算**。经常配合使用——`context` 记录/计算某个值，`condition` 依据它决定走哪条路。

## 3.1 condition — 条件分支控制

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `condition` | str | — | 条件：实体 key 或 `&{...}` 表达式 |
| `condition_not` | str | — | 反向条件（优先级高于 `condition`） |
| `condition_then` | list[str] | `[]` | 条件满足时执行 |
| `condition_else` | list[str] | `[]` | 条件不满足时执行 |

condition / condition_not 支持 `&{...}` 表达式（见第 4 章）。`condition` 的求值返回 `"True"` / `"False"` 字符串，通过 `evaluate_condition` 完成。

**裸实体 key 兼容**：不带 `&{...}` 时行为不变，`condition: my-entity` 等价于执行该实体并取其布尔值。

示例：

```ini
[auto-fight-end]
type: condition
name: 战斗结束 战斗胜利 或者 失败
condition: &{condition-in_location-fight-over-win | condition-in_location-fight-over-loss1 | in_location-get-item}
condition_then: click-center,wait-1,click-center,wait-1,click-upcenter,condition-set-win-flag,condition-get-item-win
condition_else: wait-1,auto-fight-end

[judge-power]
type: condition
name: 判断战力
condition: &{get-combat-power >= 50000}
condition_then: start-fight
condition_else: refresh-opponent
```

**可用作条件操作数的元素**（`&{...}` 内）：

| 元素 | 说明 |
|------|------|
| `entity_key` | 执行该实体，返回值作为操作数 |
| `${section:option}` | 从配置读取值 |
| `@{entity_key}` | 执行实体并读取返回值 |
| `%{context_key}` | 读取上下文变量（支持表达式） |
| `123` / `3.5` | 数值字面量 |
| `&` `|` | 逻辑与 / 或 |
| `>=` `<=` `>` `<` `==` `!=` | 比较 |
| `()` | 分组括号 |

优先级（低→高）：`|` → `&` → 比较 → `()`

## 3.2 context — 上下文变量运算

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `context_get` | str | — | 读取的上下文变量 key |
| `context_default` | str | `""` | 变量不存在时的默认值 |
| `context_default_type` | str | `str` | **输入**类型：`str`/`int`/`float`/`bool` |
| `context_type` | str | `str` | **输出**类型转换（存 context_key 前）：`str`/`int`/`float`/`bool` |
| `action` | list[str] | `[]` | **运算链**（非执行链），格式 `运算符\|值` |
| `values` | list[str] | `[]` | 批量初始化多个变量（`k=v` 逗号分隔） |

### 运算链运算符

| 类型 | 运算符 | 说明 | 示例 |
|------|--------|------|------|
| int/float | `+` `-` `x` `/` | 算术 | `+|1`、`x|2`、`/|3` |
| int/float | `=` | 赋值 | `=|100` |
| int/float | `==` `>` `<` `>=` `<=` | 比较（返回 bool） | `>|5` |
| str | `+` | 拼接 | `+|abc` |
| str | `=` `==` | 赋值 / 相等 | `=|新值` |
| str | `contains` | 是否包含（返回 bool） | `contains|关键词` |

类型规则：int + float → float，int x int → int，int / int → float。

**批量初始化**（设变量，不触发 method）：

```ini
[init-params]
type: context
values: base=buttons\a.png, neighbor=locations\b.png
```

### 用 context_key 存储实体返回值

任何实体（click/match/ocr/func）都能通过 `context_key` + `context_type` 把返回值存入上下文：

```ini
[in_location-get-item]
extend: in_location
target: buttons\getItem.png
context_key: in_getItem_flag
context_type: bool

[context-fight-is-win]
type: context
context_get: win_flag
context_type: bool
context_default: True
context_key: win_flag
```

`context_get` / `context_key` 可配合实现"读变量 → 运算 → 写回"的模式。

### 调试输出

使用 `context_print` 方法打印当前全部上下文变量：

```ini
[debug-ctx]
type: func
func: context_print
```

输出格式：`上下文变量 (3)：\n  power_value = 3693 (int)\n  win_flag = True (bool)\n  name = 物品A (str)`

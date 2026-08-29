# 第 2 章 click / match / ocr

三者都是"读屏幕"的实体。click 找到图就点，match 只找图不点返回坐标，ocr 找到区域再识别文字。注意区分。

## 2.1 click — 模板匹配 + 点击

点击优先级：`pos` > `match`（+ `target`）> `target`（单独）。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `target` | str | — | 匹配的图片路径（支持 `${}` `@{}` 占位符） |
| `pos` | list[int] | `[]` | 直接点击坐标 `[x, y]`，设置后跳过所有匹配 |
| `match` | str | — | 引用 `match` 实体，对其结果坐标点击；与 `target` 同时设置时触发级联匹配 |
| `per` | float | `0.8` | 匹配阈值 |
| `max_wait` | int | — | 最大等待秒数 |
| `break_point` | str | `off` | 超时是否跳出：`on`/`off` |
| `index` | int | `0` | 多匹配时取第几个结果（级联模式下为全局子匹配索引） |
| `condition` | str | — | 前置条件：实体 key 或 `&{...}` 表达式 |
| `condition_not` | str | — | 反向条件（优先级高于 `condition`） |
| `condition_then` | list[str] | `[]` | 条件满足时执行的实体 |
| `condition_else` | list[str] | `[]` | 条件不满足时执行的实体 |
| `wait_sec` | list[str] | `[]` | 匹配等待期间每轮执行的操作 |

示例：

```ini
[click-fight]
type: click
name: 出击
target: buttons\fight.png
wait_target: buttons\activities.png
max_wait: 10
sleep: 2
```

**`match` + `target` 级联匹配**：两者同时设置时，先执行 `match` 定位大区域（可能多个），再在每个区域内用 `target` 图片做二次模板匹配，全部子匹配按区域顺序排列。`index` 选择第 N 个子匹配点击。

示例：match 命中 (A, B, C)，target 二次匹配得 (A0,A1,B0,C0,C1,C2)，`index=2` → 点击 B0。

## 2.2 match — 纯模板匹配（不点击）

`match` 执行**纯模板匹配**，在屏幕上查找图片并返回坐标信息，**不执行点击**。返回的 `MatchTemplete` 对象可被 `click`、`ocr` 等通过 `match` 字段引用。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `match` | str | — | 引用 `match` 实体 key，与 `target` 同时设置时触发级联匹配（不点击，仅检测） |
| `target` | str | — | 匹配的模板图片路径（相对于 `resources/`） |
| `per` | float | `0.8` | 匹配阈值（`cv2.TM_CCOEFF_NORMED`） |
| `action` | list[str] | `[]` | **变换操作**（非执行链），见下 |

### 执行流程

1. `testFor_before` 门控（若配置）→ 等待前置图片出现
2. `pre_sleep` 等待
3. `cv2.matchTemplate` 全屏匹配 → 去重（邻近 10px 内只保留一个）
4. 按 `action` 列表依次对匹配结果应用变换操作
5. `sleep` 等待
6. `wait_target` 等待（若配置）
7. 输出 `log` 消息（若配置）
8. `testFor_after` 复检（若配置）→ 不匹配则重试

### 变换操作（action）

`action` 在此类型中**不是执行链**，而是对匹配区域进行位置/尺寸变换的操作序列。多个操作用逗号分隔，依次应用到匹配结果上。所有操作使用 `|` 作为分隔符。

**整体平移（相对于模板尺寸）：**

| 操作 | 格式 | 效果 | 计算公式 |
|------|------|------|----------|
| 上移 | `up\|N` | 匹配区域向上偏移 | `shift_y = -模板高度 × N` |
| 下移 | `down\|N` | 匹配区域向下偏移 | `shift_y = 模板高度 × N` |
| 左移 | `left\|N` | 匹配区域向左偏移 | `shift_x = -模板宽度 × N` |
| 右移 | `right\|N` | 匹配区域向右偏移 | `shift_x = 模板宽度 × N` |

**单边移动（像素级别，支持负数向内收缩）：**

| 操作 | 格式 | 效果 | 计算公式 |
|------|------|------|----------|
| 上边移动 | `up-M\|N` | 上边向上移动 N px | `y0 = y0 - N` |
| 下边移动 | `down-M\|N` | 下边向下移动 N px | `y1 = y1 + N` |
| 左边移动 | `left-M\|N` | 左边向左移动 N px | `x0 = x0 - N` |
| 右边移动 | `right-M\|N` | 右边向右移动 N px | `x1 = x1 + N` |

> N 为负值时向内收缩（如 `right-M|-15` 表示右边向上收缩 15px）。

**整体缩放（相对于模板尺寸）：**

| 操作 | 格式 | 效果 | 计算公式 |
|------|------|------|----------|
| 横向缩放 | `reW\|N` | 宽度缩放 | `新宽度 = 原宽度 × N` |
| 纵向缩放 | `reH\|N` | 高度缩放 | `新高度 = 原高度 × N` |

> N 为数字（整数或浮点数，如 `1.5`、`0.8`、`30`、`-20`）。转换类以模板尺寸为基数，边移动类以像素为单位。变换在匹配结果的四个角点和中心点上同步生效。整体平移与单边移动可混合使用（按 `action` 顺序依次生效），但**不能与缩放混合**（后执行覆盖前者）。推荐在缩放后另开一个 `match` 实体做边调整。

**变换示例：**

```ini
[find-power-icon]
type: match
target: buttons\power_icon.png
action: down|1.5, reW|2.0, reH|1.2

[match-offset-region]
type: match
target: buttons\icon.png
action: right-M|30, down-M|-15
; 右边向右扩展 30px，下边向上收缩 15px
```

### 返回值

- 匹配成功：`MatchTemplete` 对象（`matched=True`，含 `matchTempleteCenterPoints` 中心点坐标列表）
- 匹配失败：`None`

### 不支持的字段

对 `match` 无效：`pos`、`index`、`func`、`args`、`condition*`、`break_point`、`wait_sec`。

### 级联匹配（match + target）

```ini
# 级联检测：先找大区域 power-panel，再检测区域内是否有 power-icon
[check-power-in-region]
type: match
match: find-power-panel
target: buttons\power_icon.png

# 用作条件判断（None → 条件不满足）
[guard-power]
type: condition
condition: check-power-in-region
condition_then: do-something
```

## 2.3 ocr — 匹配 + 裁剪 + OCR

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `target` | str | — | 匹配后裁剪并 OCR 的图片 |
| `match` | str | — | 引用 `match` 实体，对其结果区域 OCR |
| `per` | float | `0.8` | 匹配阈值 |

优先级：`match` > `target`。

```ini
[ocr-power-value]
type: ocr
name: 识别战力值
match: find-power-icon
context_key: combat_power
context_type: int

[judge-power]
type: context
name: 判断战力是否足够
context_get: combat_power
context_default: 0
context_default_type: int
action: >=|50000
context_key: is_strong
```

## 2.4 图片资源

- 路径相对于 `jczx/resources/`，如 `buttons\login.png`。
- 格式：PNG，以 `cv2.imread(..., IMREAD_GRAYSCALE)` 读取。
- 初始化时 `target`、`testFor_before`、`testFor_after` 自动加载到缓冲池。
- 目录：`buttons/`（按钮）、`locations/`（位置、红点等）、`numbers/`（免 OCR 数字识别）、`roles/`（角色）、`orders/`（订单）。

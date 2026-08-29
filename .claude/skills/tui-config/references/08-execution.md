# 第 8 章 执行流程与调试

## 8.1 模板方法 `_exec_entity`

所有实体由 `_exec_entity(entity, on_exec)` 模板方法统一管控：

```
_exec_entity(entity, on_exec)
  for times:
    [stop_check]
    [testFor_before 门控]    ← testFor_pre_sleep → wait → testFor_sleep
    pre_sleep
    on_exec(entity)          ← 类型特有逻辑
    sleep
    [wait_target 等待]         ← 等待指定图片出现，受 max_wait 约束
    log 输出                 ← entity.log 解析占位符后打印
    [action 链]              ← get_next() → 递归 exec
    [testFor_after 复检]     ← 不可见 → continue 重试
```

`wait_target` vs `testFor_after`：`wait_target` 仅等待不重试，超时后继续执行 action 链；`testFor_after` 不可见时重新执行整个实体（含 pre_sleep/on_exec）。

## 8.2 各类型特有逻辑

| 类型 | 特有逻辑 | testFor | action 链 |
|------|---------|---------|-----------|
| task | 遍历 `entity.action` 执行子实体 | — | ✗（已内联） |
| func | 调用 `JCZXGaming` 方法 | — | ✓ |
| click | pos / match / target 点击 | ✓ | ✓ |
| dynamic | 遍历 action → 二次 exec | — | ✗ |
| match | findImageDetail + 变换 | — | ✗ |
| ocr | match / target 定位 + OCR | ✓ | ✓ |
| context | 读取变量 + 运算链 | ✓ | ✗ |
| condition | 评估条件 → then/else | ✓ | ✓ |

顶层入口 `exec_task_raw()` 在前后清空上下文变量，确保任务间上下文隔离。

## 8.3 门控字段

| 字段 | 说明 |
|------|------|
| `testFor_before` | 执行前检测图片，不可见则跳过实体 |
| `testFor_after` | action 链后检测图片，不可见则重试 |
| `testFor_max_wait` | testFor_before 最大等待秒数。click 中为 0 时沿用 `max_wait` |
| `testFor_pre_sleep` | testFor_before 前的等待 |
| `testFor_sleep` | testFor_before 通过后的等待 |
| `testFor_per` | testFor_before 匹配阈值（默认 0.8） |
| `wait_target` | 实体主逻辑完成后等待的图片路径，支持占位符。超时受 `max_wait` 约束 |
| `wait_target_per` | wait_target 匹配阈值（默认 0.8） |
| `wait_target_sleep` | wait_target 匹配到后的等待秒数（未匹配超时则不等待） |
| `max_wait` | wait_target / click 最大等待秒数。`0` 表示不等待 |

## 8.4 截图缓存

同帧内多个实体共享截图，默认 TTL 500ms。click/swipe/drag 后自动失效。链顶层设置 `screen_cache_ttl`，子实体 `-1` 自动继承，无需每个都配置。

| `screen_cache_ttl` | 含义 |
|-------------------|------|
| `-1` | 继承上级（默认） |
| `0` | 禁用（息屏/动画场景，每次强制刷新） |
| `N` | 自定义毫秒值 |

## 8.5 调试与日志

- `debug.screenshot.mode`（Config.txt）：`off`/`simple`（连续截图）/`annotated`（标注匹配/点击/OCR 位置），输出至 `screenHistory/`。
- 用 `context_print` 打印上下文（`func`）。
- 用 `log` 字段辅助诊断：支持四种占位符（见第 4 章），`log_level` 控制输出等级。
- 日志写在工作区根目录：`JczxCli.log`、`JczxTUI.log`。

## 8.6 常见问题排查

| 现象 | 可能原因 | 处理 |
|------|---------|------|
| 点击/匹配找不到图 | `per` 太低 / 图片路径错 / 屏幕分辨率不匹配 | 检查路径、调低 `per`、看 `annotated` 截图 |
| 实体 lookup 失败 | 逗号后带空格，拆出 `" b"` | 去掉逗号后的空格 |
| 动作太慢 | `sleep`/`max_wait` 过长，或截图缓存被禁用 | 调小 sleep，确认 `screen_cache_ttl` 合理 |
| 条件永远不满足 | 返回值是 `None`（match 失败）或被当作空串 | 检查 match 是否命中，`context_default` 是否设置 |
| 任务不进列表 | `view` 不是 `on`，或 method/call 类型 | `view: on` 才是 TUI 任务 |
| 同名 section 报错 | 子文件与 MainMenu key 冲突 | 改 key 避免冲突 |

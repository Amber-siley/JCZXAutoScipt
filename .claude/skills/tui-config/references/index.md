# 任务配置书籍目录

本目录是 JCZXAutoScript TUI 任务配置规则的**书籍目录**。像一本书按章节组织，每章一个 md 文档。**写任何配置前先读本目录**，按需跳到对应章节。

> 权威源头是仓库根目录 `TASK_CONFIG_GUIDE.md`，references 各章是对它的分类整理与选摘。字段细节如需交叉验证，回查该文档与 `jczx/configEntity.py` 的 `JczxSectionEntity`（字段定义）、`jczx/jczxCli.py`（引擎行为）。

## 章节速览

| 章 | 主题 | 什么时候打开 |
|----|------|-------------|
| 第 1 章 | [语法与类型总览](01-syntax.md) | 写任何实体前，确认语法和字段系统 |
| 第 2 章 | [click / match / ocr](02-click-match.md) | 要做点击、模板匹配、OCR 识别时 |
| 第 3 章 | [condition / context](03-condition-context.md) | 要做分支判断、记录/运算状态变量时 |
| 第 4 章 | [占位符解析](04-placeholders.md) | 要用 `${}` `@{}` `%{}` `&{}` 引用配置/实体/变量/表达式时 |
| 第 5 章 | [多文件配置](05-multifile.md) | 要拆分任务、新增子文件、继承公共实体时 |
| 第 6 章 | [method / call](06-method-call.md) | 要复用一段带参数的执行链时 |
| 第 7 章 | [任务设置表单](07-settings.md) | 要配 TUI 界面里可调的参数时 |
| 第 8 章 | [执行流程与调试](08-execution.md) | 要调时序、testFor/wait_target/截图缓存行为时 |
| 第 9 章 | [可用 func 方法](09-func.md) | 要调引擎内置方法时 |
| 第 10 章 | [完整示例](10-examples.md) | 想看整体写法的样板 |

## 快速决策

**我要做的是……**

- **点一个按钮** → 第 2 章 click。用 `target` 指定图片，可能加 `pos` 或 `match` 级联。
- **判断屏幕上有没有某个图** → 第 2 章 match，或第 3 章 condition 引用 match。
- **识别一段数字/文字** → 第 2 章 ocr，配合 `context_key` 存结果。
- **按情况走不同分支** → 第 3 章 condition + `condition_then`/`condition_else`。
- **记录并运算某个值** → 第 3 章 context + `action` 运算链。
- **引用别的值/配置/实体结果** → 第 4 章占位符。
- **复用一段执行链** → 第 6 章 method/call。
- **让用户能在界面改参数** → 第 7 章 settings/setting。
- **把任务拆到单独文件** → 第 5 章多文件。
- **调等待/匹配时序** → 第 8 章执行流程。

## 读法建议

- 配置是**声明式的**：每一个 `[key]` 是一节，描述一个"实体"，引擎按 `action` 串起来执行。
- 关键心智模型：**实体返回一个结果**（坐标/文本/布尔/`None`），下一个实体通过 `action` 链或占位符消费它。
- 三种"伪 action"容易混淆：`match` 的 `action`=坐标变换、`context` 的 `action`=数值运算、`dynamic` 的 `action`=循环源。动它们前先看对应章，别当成执行链。

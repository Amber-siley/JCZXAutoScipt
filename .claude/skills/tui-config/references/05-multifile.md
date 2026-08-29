# 第 5 章 多文件配置

通过 `type: file` 将任务拆分到独立子文件中，MainMenu.txt 仅保留公共实体和入口声明。

## 5.1 使用方式

```ini
/ MainMenu.txt - 入口声明
[jjc-file]
type: file
target: tasks\jjc.txt
name: 竞技场日常
```

| 字段 | 说明 |
|------|------|
| `type` | `file` |
| `target` | 子文件路径（相对于 `Config/`），支持 `${}` 占位符 |
| `name` | 注释用显示名（不影响逻辑） |

## 5.2 子文件格式

与 MainMenu.txt 完全相同，可包含任意类型实体。外部实体可通过 `extend` 跨文件继承 MainMenu 中的公共实体，`action` 链也可引用 MainMenu 中的实体。

```ini
/ tasks/jjc.txt
[jjc-simulate]
type: task
name: 竞技场日常
action: goto-jjc,condition-need-fight
settings: settings-jjc

[click-jjc]
type: click
target: buttons\competition.png
```

## 5.3 约束

- **冲突检测** — 任意两个文件出现同名 section 时报 `ValueError`，不静默覆盖。所以新增任务时 key 不能与 MainMenu 或其他子文件重复。
- **不能嵌套** — 子文件中 `type: file` 被忽略。
- **Settings 持久化** — 外部 task 的设置保存到其来源文件，不污染 MainMenu.txt。
- **公共实体** — `in_location`、`click-center`、`goto-home`、`auto-fight` 等跨任务复用的实体保留在 MainMenu 中。

## 5.4 推荐目录结构

```
Config/
  MainMenu.txt          ← 公共实体 + file 入口
  Config.txt            ← 全局设置
  tasks/
    jjc.txt             ← 竞技场日常
    inllusion.txt       ← 虚影周本
    Favor.txt           ← 好感任务
    receive.txt         ← 领取各种东西
    Construction.txt    ← 基建相关
```

## 5.5 任务队列

队列在 `Queues.txt`，`[queue-xxx]` 内 `tasks:` 逗号列表，按顺序执行。队列引用的 task key 需存在（通常是 `view: on` 的入口 task）。

```ini
[queue-daily]
name: 日常
tasks: launch-game,task-receive-everyday,jjc-simulate,goto-inllusion,task-receive-mail,task-get-ore,task-receive-dayAndWeek,task-receive-ExplorationGuidelines
```

## 5.6 新增子文件流程

1. 在 `jczx/Config/tasks/` 新建 `<模块>.txt`。
2. 在 MainMenu.txt 末尾加一个 `type: file` 入口，`target` 指向新文件。
3. 若该文件里有需要 `settings` 持久化的 task，确保 settings 定义在来源文件内。
4. 检查 key 无冲突（全局同名会抛 `ValueError`）。

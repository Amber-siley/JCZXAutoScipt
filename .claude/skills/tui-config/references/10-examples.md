# 第 10 章 完整示例

以下示例取自项目真实配置，作为整体写法的样板。

## 10.1 启动游戏（MainMenu.txt）

```ini
[launch-game]
type: task
view: on
name: 启动-游戏
action: launch-game-plan

[launch-game-plan]
type: func
func: start_game
args: com.megagame.crosscore,com.megagame.crosscore/com.mjsdk.app.MJUnityActivity
action: user-login
sleep: 30

[user-login]
type: click
name: 点击登录
testFor_before: locations\onUseLogin.png
testFor_per: 0.7
condition: condition-start-game
condition_then: click-start-game,wait-5,goto-home
condition_else: click-userLogin,click-start-game,wait-5,goto-home
max_wait: 3000

[condition-start-game]
type: func
func: in_location
target: buttons\login.png

[click-start-game]
type: click
name: 开始游戏
target: buttons\login.png
action: no-reminders
max_wait: 300

[no-reminders]
type: click
name: 不再提醒
target: buttons\noReminders.png
action: close-Notice
break_point: on
max_wait: 30

[close-Notice]
type: click
name: 关闭公告
target: buttons\closeNotice.png
```

## 10.2 testFor_before / testFor_after

```ini
[check-and-claim-reward]
type: click
name: 领取奖励
target: buttons\claim.png
testFor_before: buttons\reward_panel.png
testFor_after: buttons\reward_available.png
testFor_max_wait: 5
max_wait: 10
break_point: on
action: claim-next-reward
```

1. 等 `reward_panel.png` 出现（最多 5s），不出现则跳过
2. 匹配点击 `claim.png`（最多 10s）
3. 执行 `claim-next-reward`
4. 复检 `reward_available.png`，不可见则回到步骤 1

## 10.3 OCR + 上下文运算

```ini
[find-power-icon]
type: match
target: buttons\power_icon.png
action: down|1.5,reW|2.0,reH|1.2

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

## 10.4 condition 独立使用

```ini
[judge-power]
type: condition
name: 判断战力
condition: &{get-combat-power >= 50000}
condition_then: start-fight
condition_else: refresh-opponent
testFor_before: buttons\arena_panel.png
testFor_max_wait: 5
```

## 10.5 自动战斗（MainMenu.txt）— 条件循环

```ini
[auto-fight]
type: task
view: off
name: 自动战斗
action: click-skip-animation,click-auto-fight,auto-fight-end,wait-5

[auto-fight-end]
type: condition
name: 战斗结束 战斗胜利 或者 失败
condition: &{condition-in_location-fight-over-win | condition-in_location-fight-over-loss1 | in_location-get-item}
condition_then: click-center,wait-1,click-center,wait-1,click-upcenter,condition-set-win-flag,condition-get-item-win
condition_else: wait-1,auto-fight-end
```

`auto-fight-end` 的 `condition_else` 里引用了自身（`auto-fight-end`），实现"不结束就再判断"的循环。

## 10.6 拆分到子文件并引用（receive.txt）

```ini
/ tasks/receive.txt - 领取各种东西
[task-receive-everyday]
type: task
view: on
name: 领取每日礼包
action: goto-home,goto-supplyStation,click-giftPackage,wait-5,condition-to-get-freePackage

[goto-supplyStation]
type: click
name: 补给站
target: buttons\supplyStation.png
wait_target: buttons\giftPackage.png

[condition-to-get-freePackage]
type: condition
name: 条件判断是否有免费礼包
condition: condition-in_location-freePackage
condition_then: click-free-giftPackage,condition-to-purchase,goto-home
condition_else: goto-home
```

MainMenu.txt 对应入口：

```ini
[file-receive-task]
type: file
target: tasks\receive.txt
name: 领取各种东西
```

## 10.7 任务设置表单（settings/setting）

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

# Lochfolk Prinzessin Simulator (LPSim): 水皇模拟器，一个七圣召唤模拟器

---

[![Coverage Status](https://coveralls.io/repos/github/LPSim/backend/badge.svg?branch=master)](https://coveralls.io/github/LPSim/backend?branch=master)
[![PyPI version](https://img.shields.io/pypi/v/lpsim.svg?color=blue)](https://pypi.org/project/lpsim/)

### [**English README**](README.en.md)

该仓库为水皇模拟器的后端，用来模拟七圣召唤对局，使用Python 3.10编写，使用Pydantic和FastAPI。项目另有一个[前端仓库](https://github.com/LPSim/frontend)，包含可以与该后端交互的前端页面。

该项目使用AGPL-3.0协议。如果您有任何基于此项目的二次开发和分发，请遵守该协议。

## 声明

本项目仅供学习交流使用，前端界面仅用于展示对局状态和方便代码调试，请在下载后24小时内删除相关内容。所有相关代码基于AGPLv3协议开源。项目与米哈游公司无关，所有游戏素材版权归米哈游公司所有。本项目及其代码仓库中不包含米哈游具有版权的图像素材，或是任何与米哈游产品相关的非公开信息。

## 项目进度

以实现所有4.3版本及以前的角色和卡牌，包括平衡性调整。

:sparkles: NEW: 4.3版本角色和卡牌，以及平衡性调整已实现。

## 特性

- 已实现所有截止当前版本的角色和卡牌，包括其历史版本。
- 支持在同一套卡组中使用不同版本的角色和卡牌。
- 支持作为一个小型服务器与客户端交互。
- 提供了一个前端用来与服务器交互。
- 可以从任意状态加载并继续运行，保持结果不变。
- 100%代码覆盖率。

## 使用方法

该项目需要Python 3.10或更新版本。

### 使用pip安装

使用`pip install lpsim`安装最新的发布版本。你可以在[PyPI](https://pypi.org/project/lpsim/)找到最新的发布版本，在[CHANGELOG.md](CHANGELOG.md)找到更新日志。

使用`pip install lpsim -i https://test.pypi.org/simple/`安装最新的开发版本。当新的提交被推送到`master`分支并通过所有测试时，新的版本将会被发布到Test PyPI。当新的版本tag被推送到`master`分支时，新的版本将会被发布到PyPI。

### 使用源码安装

克隆该仓库并使用`pip install .`安装。

### HTTP服务器

#### 对局服务器

使用FastAPI提供一个HTTP对局服务器，用来与客户端交互。使用以下命令运行服务器：
```
from lpsim.network import HTTPServer
server = HTTPServer()
server.run()
```

它将在`localhost:8000`上开启一个FastAPI服务器，并接受任意来源的连接。在初始化HTTPServer时，你可以设置卡组和对局配置来创建一个带有指定规则的对局。

启动服务器后，打开[前端页面](https://lpsim.zyr17.cn/index.html)，在右上角修改服务器URL（默认为`http://localhost:8000`），按照页面上的指示设置卡组，并开始对局。

目前异常处理比较混乱，错误可能导致游戏状态变为ERROR，服务器抛出异常，客户端返回空响应，返回404/500，或者前端运行JS失败。请打开前端的控制台，并在前端后后端查看错误信息。

#### 房间服务器

你可以使用房间服务器来提供多个对局。它管理多个HTTP服务器实例，前端可以创建新的房间或加入已有的房间。当一个新的房间被创建时，房间服务器会告诉前端房间名和它运行的端口，然后前端会连接到该端口上的HTTP服务器。当一个房间创建了很长时间并且没有收到POST请求时，它会自动关闭。更多细节请参考`lpsim/network/http_room_server.py`和`http_room_serve.py`。

### 非交互对局

非交互对局主要用于代码测试和AI训练。你可以按照下述流程进行。

#### 定义卡组

开始对局之前，需要先定义卡组。卡组可以使用文本或JSON格式定义。通常使用`Deck.from_str`就足够了，它可以定义角色和卡牌，以及控制它们的版本。下面的示例代码中的卡组字符串展示了卡组定义的语法，所有卡牌都使用4.1版本，除了风与自由，它使用4.0版本（因为它在3.7版本之后没有改变，当指定4.0版本时，卡组会自动选择3.7版本）。同时，也支持使用牌组分享码导入牌组。更多细节请参考`server/deck.py`。

#### 开始对局

1. 初始化一个新的`server.Match`实例。
2. 使用`set_deck`函数为玩家分配卡组。
3. 如果需要，修改`Match.config`。
4. 卡组设置完成后，使用`Match.start`函数开始对局。它会根据配置和卡组初始化对局。如果出现错误（例如卡组不合法），它会返回False和具体错误信息。
5. 使用`Match.step`函数推进对局。默认情况下，该函数会持续执行，直到对局结束或者生成需要响应的请求。

为了更方便的响应请求，在`agents`模块中项目包含了一些简单的代理。这些代理可以响应各种请求。特别的，`InteractionAgent`可以解析命令行并生成响应，使用命令行交互时较为方便。同时，该代理也是前端和后端交互时使用的代理。

#### 示例代码

```python
from lpsim import Match, Deck
from lpsim.agents import RandomAgent
deck_string = '''
default_version:4.1
charactor:Fischl
charactor:Mona
charactor:Nahida
Gambler's Earrings*2
Wine-Stained Tricorne*2
Vanarana
Timmie*2
Rana*2
Covenant of Rock
Wind and Freedom@4.0
The Bestest Travel Companion!*2
Changing Shifts*2
Toss-Up
Strategize*2
I Haven't Lost Yet!*2
Leave It to Me!
Calx's Arts*2
Adeptus' Temptation*2
Lotus Flower Crisp*2
Mondstadt Hash Brown*2
Tandoori Roast Chicken
'''
deck0 = Deck.from_str(deck_string)
deck1 = Deck.from_str(deck_string)
match = Match()
match.set_deck([deck0, deck1])
match.start()
match.step()

agent_0 = RandomAgent(player_idx = 0)
agent_1 = RandomAgent(player_idx = 1)

while not match.is_game_end():
    if match.need_respond(0):
        match.respond(agent_0.generate_response(match))
    elif match.need_respond(1):
        match.respond(agent_1.generate_response(match))
    match.step()

print(f'winner is {match.winner}')
```

### 自定义角色和卡牌

自定义角色和卡牌前，你需要了解actions, event handlers和value modifiers。所有与对局的交互（一个实例需要修改对局中其他实例的状态）都是通过actions完成的，所有的actions都是由events触发的。value modifiers用来修改值，例如骰子消耗和伤害数值/类型。最简单的实现一个新的对象的方法是参考并复制一个已有的卡牌/角色/技能/状态...并修改它。你可以在细节中找到更多信息。

`templates/charactor.py`是一个角色的模板。你可以复制它并修改它来实现一个新的角色。你可以定义任何与角色相关的对象，例如技能、天赋、召唤、状态。然后，你需要为这些对象创建描述，描述将会在前端中使用，class registry会拒绝没有描述的对象。最后，使用`register_class`函数将所有对象以及它们的描述注册到class registry中，就可以在对局中使用它们了。注意，模板使用了relative import，因为它用来创建新的官方角色。如果你想在项目外创建一个新的自定义角色，你需要将它们改为absolute import。

定义一个新的卡牌相对简单，你可以参考`templates/card.py`，它定义了一个新的卡牌“大心海”，它消耗2个任意骰子并抽3张牌。作为自定义卡牌的示例，在这个文件里使用了absolute import，因此可以在项目外直接使用。

你可以手动注册新的对象并在对局中使用它们。以“大心海”为例，首先安装`lpsim`，然后在`import lpsim`之后输入`import templates.card`。然后你可以通过`a = HTTPServer(); a.run()`创建一个HTTP服务器，你会发现修改卡组时一个新的卡牌被添加到了候选卡牌列表中。总代码如下，在项目根目录运行：

```python
import lpsim
import templates.card
a = lpsim.HTTPServer()
a.run()
```

## 细节

使用Pydantic保存和加载对局状态，导出的数据可以用来恢复对局到某个状态并继续运行，也可以用来渲染前端的对局状态。

兼容不同版本的角色和卡牌。例如你可以开启一个3.8版本的双岩一斗和3.3版本的双岩剑鬼的对局，或者使用3.3的神宵和3.7的申鹤配合4.3的新行动牌和装备。

通过`request`和`response`来交互。当`request`列表不为空时，代理需要响应其中的一个请求。当多个玩家需要响应时（例如在游戏开始时选择角色和卡牌），它们的请求会同时生成。

对局中的所有修改都是通过`action`来实现的。每个`action`都会触发一个事件，并且可能会激活后续的`action`。这些新激活的`action`会被添加到现有的`action`列表的顶部，类似于堆栈列表的结构，参考`EventFrame`类的实现。

对局中所有的对象包含两种触发器：event handlers和value modifiers。事件处理器用来监控事件并产生响应的`action`列表。值修改器用来修改可变值并在必要时更新内部状态。可修改的值包括初始骰子颜色、伤害和消耗等。

所有的代码都使用pytest进行测试，覆盖率100%（除了防御性代码，它们被标记为`# pragma: no cover`）。由于完全兼容不同版本，当实现了新的版本时，所有已有测试都应该通过而不需要修改。

## 贡献

欢迎合作开发项目代码，但是目前没有详细的贡献指南。如果你想添加新的角色相关的对象（角色、技能、天赋、召唤、状态），请参考`server/charactor/template.py`和已经实现的角色。如果你想添加新的卡牌，请参考`server/card`中已经实现的卡牌。

你可以通过QQ群945778865联系作者，咨询开发和使用上的问题，进群问题的答案是模拟器的中文名。

开发这个项目花费了大量(本来用来打牌和打模拟宇宙的)时间。如果你觉得这个项目有帮助，您可以通过微信支持作者。

<p align="center">
    <img src="docs/wechat.png" alt="wechat" width="150">
</p>
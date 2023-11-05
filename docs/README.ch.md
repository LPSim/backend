# Lochfolk Prinzessin Simulator (LPSim): 水皇模拟器，一个七圣召唤模拟器

---

[![Coverage Status](https://coveralls.io/repos/github/LPSim/backend/badge.svg?branch=master)](https://coveralls.io/github/LPSim/backend?branch=master)
[![PyPI version](https://img.shields.io/pypi/v/lpsim.svg?style=flat-square&color=blue)](https://pypi.org/project/lpsim/)

该仓库为水皇模拟器的后端，用来模拟七圣召唤对局，使用Python 3.10编写，使用Pydantic和FastAPI。

该项目使用AGPL-3.0协议。

## 项目进度

以实现所有4.1版本及以前的角色和卡牌，包括平衡性调整。

:sparkles: NEW: 4.2版本角色和卡牌，以及平衡性调整以实现。

## 特性

- 所有4.1版本及以前的角色和卡牌已实现。
- 支持在同一套卡组中使用不同版本的角色和卡牌。
- 支持作为一个小型服务器与客户端交互。
- 提供了一个前端用来与服务器交互。
- 可以从任意状态加载并继续运行，保持结果不变。
- 100%代码覆盖率。

## 使用方法

该项目需要Python 3.10或更新版本。

### 使用pip安装

使用`pip install lpsim`安装最新的发布版本。你可以在 [PyPI](https://pypi.org/project/lpsim/)找到最新的发布版本，你可以在 [CHANGELOG.md](CHANGELOG.md)找到更新日志。

使用`pip install lpsim -i https://test.pypi.org/simple/`安装最新的开发版本。 当新的提交被推送到`master`分支并通过所有测试时，新的版本将会被发布到测试 PyPI。当新的版本tag被推送到`master`分支时，新的版本将会被发布到PyPI。

### 使用源码安装

克隆该仓库并使用`pip install .`安装。可能缺失`src/lpsim/_version.py`导致 `setuptools-scm`报错，可以手动创建该文件并写入：
```python
__version__ = 'unknown'
__version_tuple__ = (0, 0, 0)
```

### HTTP服务器

使用FastAPI提供一个HTTP服务器，用来与客户端交互。使用以下命令运行服务器：
```
from lpsim.network import HTTPServer
server = HTTPServer()
server.run()
```

它将在`localhost:8000`上开启一个FastAPI服务器，并接受任意来源的连接。在 初始化HTTPServer时，你可以设置卡组和对局配置来创建一个带有指定规则的对局。

启动服务器后，打开[前端页面](https://lpsim.zyr17.cn/index.html)，在右上角 修改服务器URL（默认为`http://localhost:8000`），按照页面上的指示设置卡组， 并开始对局。

目前异常处理比较混乱，错误可能导致游戏状态变为ERROR，服务器抛出异常，客户端 返回空响应，返回404/500，或者前端运行JS失败。请打开前端的控制台，并在前端后后端查看 错误信息。

### 非交互对局

#### 定义卡组

开始对局之前，需要先定义卡组。卡组可以使用文本或JSON格式定义。通常使用 `Deck.from_str`就足够了，它可以定义角色和卡牌，以及控制它们的版本。下面的 示例代码中的卡组字符串展示了卡组定义的语法，所有卡牌都使用4.1版本，除了 风与自由，它使用4.0版本（因为它在3.7版本之后没有改变，当指定4.0版本时，卡组 会自动选择3.7版本）。更多细节请参考`server/deck.py`。

#### 开始对局

1. 初始化一个新的`server.Match`实例。
2. 使用`set_deck`函数为玩家分配卡组。
3. 如果需要，修改`Match.config`。
4. 一旦卡组被设置，使用`Match.start`函数开始对局。它会根据配置和卡组初始化 对局。如果出现错误（例如卡组不合法），它会打印错误信息并返回False。
5. 使用`Match.step`函数推进对局。默认情况下，该函数会持续执行，直到对局结束 或者生成需要响应的请求。

为了更方便的响应请求，项目包含了一些简单的代理在`agents`模块中。这些代理可以 响应各种请求。特别的，`InteractionAgent`可以解析命令行并生成响应。这在控制台 环境和前端界面中都很有用。

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

## 细节

使用Pydantic保存和加载对局状态，导出的数据可以用来恢复对局到某个状态并继续运行， 也可以用来渲染前端的对局状态。

对于不同版本的角色和卡牌具有高度的兼容性。例如，你可以开启一个3.8版本的双岩一斗和3.3 版本的双岩剑鬼的对局。

通过`request`和`response`来交互。当`request`列表不为空时，代理需要响应其中的 一个请求。当多个玩家需要响应时（例如在游戏开始时选择角色和卡牌），它们的请求 会同时生成。

对局中的所有修改都是通过`action`来实现的。每个`action`都会触发一个事件，并且 可能会激活后续的`action`。这些新激活的`action`会被添加到现有的`action`列表的 顶部，类似于堆栈列表的结构，参考`EventFrame`类的实现。

对局中所有的对象包含两种触发器：event handlers和value modifiers。 事件处理器用来监控事件并产生响应的`action`列表。值修改器用来修改可变值并在 必要时更新内部状态。可修改的值包括初始骰子颜色、伤害和消耗等。

所有的代码都使用pytest进行测试，覆盖率100%（除了防御性代码，它们被标记为 `# pragma: no cover`）。通过不同版本的兼容性，当新的版本被实现时，所有过去的 测试都应该通过而不需要修改。

## 开发

欢迎合作开发项目代码，但是目前没有详细的贡献指南。如果你想添加新的角色相关的对象 （角色、技能、天赋、召唤、状态），请参考`server/charactor/template.py`和已经实现的 角色。如果你想添加新的卡牌，请参考`server/card`中已经实现的卡牌。

你可以通过QQ群945778865联系作者，咨询开发和使用上的问题，进群问题的答案是模拟器的中文名。

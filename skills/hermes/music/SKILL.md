---
name: music
description: 在本机后台播放网络音乐并控制播放状态。适用于 /music ... 命令。
platform_compatibility:
  cli: true
  macos: true
---

# Music

当用户调用 `/music ...` 时，把它视为本地音乐控制命令，而不是普通聊天。

## 规则

- 永远优先执行本地 `musicctl --text ...`，不要打开浏览器。
- 不要建议下载歌曲文件到本地。
- 如果用户输入的是 `/music keyword <关键词>`，执行：

```bash
musicctl --text play "<关键词>"
```

- 如果用户输入的是 `/music hot` 或 `/music hot <lang>`，执行：

```bash
musicctl --text hot [lang]
```

- 其他控制命令直接映射：

```bash
musicctl --text pause
musicctl --text resume
musicctl --text next
musicctl --text prev
musicctl --text stop
musicctl --text status
musicctl --text volume 60
musicctl --text volume up
musicctl --text volume down
musicctl --text mute
musicctl --text unmute
musicctl --text lang
musicctl --text lang 华语
```

## 语种输入

以下中英文别名都要接受并原样传给 `musicctl`：

- 华语 / 中文 / 汉语 / mandarin / cn
- 英语 / 英文 / english / en
- 日语 / 日文 / japanese / jp
- 韩语 / 韩文 / korean / kr
- 粤语 / cantonese / yue / hk

## 输出

- 直接返回 `musicctl --text` 输出，不要额外改写。

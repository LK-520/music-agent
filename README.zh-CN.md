<p align="center">
  <img src="./assets/music-agent-mark.svg" alt="music-agent logo" width="240">
</p>

<h1 align="center">music-agent</h1>

<p align="center">
  面向 Hermes 与 OpenClaw 的本地后台音乐控制器
</p>

<p align="center">
  不开浏览器，不弹额外窗口，不落盘保存音频文件
</p>

<p align="center">
  <a href="./README.md">English README</a>
  ·
  <a href="./LICENSE">MIT License</a>
</p>

<p align="center">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-111827?style=flat-square">
  <img alt="Python" src="https://img.shields.io/badge/python-3.9%2B-2563eb?style=flat-square">
  <img alt="Player" src="https://img.shields.io/badge/player-mpv-f97316?style=flat-square">
  <img alt="Resolver" src="https://img.shields.io/badge/source-yt--dlp-16a34a?style=flat-square">
  <img alt="Hermes" src="https://img.shields.io/badge/hermes-ready-7c3aed?style=flat-square">
  <img alt="OpenClaw" src="https://img.shields.io/badge/openclaw-ready-db2777?style=flat-square">
  <img alt="Tests" src="https://img.shields.io/badge/tests-6%20passing-059669?style=flat-square">
</p>

## 项目简介

`music-agent` 是一个为终端工作流设计的本地后台音乐控制器。
它主要服务于 Hermes 和 OpenClaw 的 `/music ...` 使用体验，把 slash command、
后台播放、音源解析和中文化终端反馈连成一条清晰的链路。

## 它解决什么问题

- 在终端里直接播放网络音乐
- 让播放在本地后台完成
- 避免打开浏览器标签页
- 避免弹出额外播放器窗口
- 避免把歌曲音频文件下载到本地

## 核心能力

- 基于 `mpv` 的本地后台播放
- 支持按关键词生成最多 20 首队列
- 支持基于 KKBOX 风云榜周榜的热歌播放
- 支持热榜语种偏好：
  `华语`、`英语`、`日语`、`韩语`、`粤语`
- 音源优先级固定为：
  `YouTube -> Bilibili -> SoundCloud`
- 支持暂停、恢复、上下首、停止、状态、音量、静音、取消静音
- 适合 Hermes 的 `/music ...` 技能工作流

## 当前状态

当前本地单元测试已通过：

```bash
python3 -m unittest discover -s tests -v
```

真实播放仍然依赖本机安装这些运行时工具：

- `mpv`
- `python3 -m yt_dlp`

如果没有安装 `mpv`，播放命令会快速失败，并给出明确提示。

## README 视觉风格

这个仓库现在已经包含：

- 居中的项目主视觉
- 一排适合 GitHub 首页阅读的徽章
- 中英文双 README 入口

主视觉文件在这里：

- [`assets/music-agent-mark.svg`](./assets/music-agent-mark.svg)

## 快速开始

```bash
git clone git@github.com:LK-520/music-agent.git
cd music-agent
./scripts/install_hermes_skill.sh
musicctl --text status
```

安装脚本会完成两件事：

- 把 Hermes skill 安装到 `~/.hermes/skills/media/music`
- 把 `musicctl` 包装脚本安装到 `~/.local/bin/musicctl`

请确认 `~/.local/bin` 已经在你的 `PATH` 中。

## 环境要求

- Python 3.9+
- `mpv`
- `python3 -m yt_dlp`
- 支持 Unix Domain Socket 与本地 `mpv` 控制的系统环境

## Hermes 使用方式

装好 skill 之后，可以直接这样用：

```bash
/music keyword 周杰伦
/music keyword 稻香
/music hot
/music hot english
/music lang 粤语
/music pause
/music resume
/music status
```

## CLI 使用方式

### 关键词播放

```bash
musicctl --text play "周杰伦"
musicctl --text play "周杰伦 稻香"
musicctl --text play "Jay Chou"
```

### 热榜播放

```bash
musicctl --text hot
musicctl --text hot english
musicctl --text hot japanese
musicctl --text lang cantonese
musicctl --text hot
```

### 播放控制

```bash
musicctl --text pause
musicctl --text resume
musicctl --text next
musicctl --text prev
musicctl --text stop
musicctl --text status
```

### 音量与静音

```bash
musicctl --text volume 60
musicctl --text volume up
musicctl --text volume down
musicctl --text mute
musicctl --text unmute
```

## 支持的热榜语种

热榜功能支持用户友好的语种别名，并会自动归一化到内部枚举：

| 内部枚举 | 常见输入 |
|---|---|
| `mandarin` | `华语`, `中文`, `汉语`, `mandarin`, `cn` |
| `english` | `英语`, `英文`, `english`, `en` |
| `japanese` | `日语`, `日文`, `japanese`, `jp` |
| `korean` | `韩语`, `韩文`, `korean`, `kr` |
| `cantonese` | `粤语`, `cantonese`, `yue`, `hk` |

## 架构

```text
/music ...
  -> skill 层
  -> musicctl
  -> musicd
  -> source adapters
  -> mpv
```

### 主要模块

- `musicctl`
  CLI 入口与结果格式化
- `musicd`
  本地守护进程、队列管理与播放器协调
- `shared`
  公共数据模型、运行时路径、语种映射与工具方法
- `skills/hermes/music`
  Hermes skill 定义
- `skills/openclaw/music`
  OpenClaw skill 定义

## 仓库结构

```text
music-agent/
├── assets/
├── musicctl/
├── musicd/
├── shared/
├── skills/
├── tests/
├── scripts/
├── LICENSE
├── README.md
└── README.zh-CN.md
```

## 当前限制

- 必须安装本地 `mpv` 才能真正播放
- 搜索质量依赖上游平台的返回结果
- Bilibili 的结果天然更杂，后续还需要继续加强过滤
- 这个项目不会构建本地音乐库
- 这个项目不提供 GUI

## 开发与测试

### 运行测试

```bash
python3 -m unittest discover -s tests -v
```

### 基础自检

```bash
musicctl --text status
musicctl --text lang english
musicctl --text hot english
```

## 后续改进方向

- 继续提升关键词排序，让原唱与官方版本更靠前
- 加强音源过滤与去重
- 增加 daemon 与播放器行为的集成覆盖
- 提供更完整的 OpenClaw 打包与接入说明

## 许可证

本项目使用 [MIT License](./LICENSE)。


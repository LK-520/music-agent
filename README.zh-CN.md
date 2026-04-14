# music-agent

[English README](./README.md)

`music-agent` 是一个面向 Hermes 和 OpenClaw 的本地后台音乐控制器。
它让你可以直接在终端里播放网络音乐，不打开浏览器、不弹额外窗口，也不把音频文件保存到本地。

## 项目亮点

- 基于 `mpv` 的本地后台播放
- 用一套命令统一控制播放、队列、音量、静音和状态
- 音源优先级固定为 `YouTube -> Bilibili -> SoundCloud`
- 支持关键词点播，默认生成最多 20 首队列
- 支持 KKBOX 风云榜周榜热歌
- 支持 5 个热榜语种：
  `华语`、`英语`、`日语`、`韩语`、`粤语`
- 可直接接入 Hermes 的 `/music ...` 使用方式

## 当前状态

目前代码层面的本地单元测试已通过：

```bash
python3 -m unittest discover -s tests -v
```

但完整的真机播放仍依赖你的本地环境安装好：

- `mpv`
- `python3 -m yt_dlp`

如果没有安装 `mpv`，播放命令会直接给出明确提示，不会卡住。

## 快速预览

```bash
musicctl --text play "周杰伦"
musicctl --text play "周杰伦 稻香"
musicctl --text hot
musicctl --text hot english
musicctl --text lang 粤语
musicctl --text status
musicctl --text pause
musicctl --text resume
musicctl --text next
musicctl --text volume 60
musicctl --text mute
```

## 功能说明

### 播放能力

- 支持按关键词生成播放队列
- 支持按 KKBOX 风云榜周榜生成热歌队列
- 新的 `play` 或 `hot` 成功后会替换当前队列
- 队列默认循环播放
- 单曲失败时自动跳过

### 控制能力

- 暂停 / 恢复
- 上一首 / 下一首
- 停止播放
- 查询状态
- 设置音量 / 增减音量
- 静音 / 取消静音

### 热榜语种偏好

热榜模式支持会话级语种偏好：

- `mandarin`
- `english`
- `japanese`
- `korean`
- `cantonese`

同时支持中文和简易英文别名输入，例如：

- `华语`、`中文`、`汉语`、`mandarin`、`cn`
- `英语`、`英文`、`english`、`en`
- `日语`、`日文`、`japanese`、`jp`
- `韩语`、`韩文`、`korean`、`kr`
- `粤语`、`cantonese`、`yue`

## 架构

```text
/music ...
  -> skill 层
  -> musicctl
  -> musicd
  -> source adapters
  -> mpv
```

### 模块职责

- `musicctl`：短生命周期 CLI 客户端
- `musicd`：本地后台守护进程
- `shared`：数据模型、语种映射、运行时路径和公共工具
- `skills/hermes/music`：Hermes 技能定义
- `skills/openclaw/music`：OpenClaw 技能定义

## 环境要求

- Python 3.9+
- `mpv`
- `python3 -m yt_dlp`
- 支持 Unix Domain Socket 和 `mpv` 的本地系统环境

## 安装方式

### 面向 Hermes 用户的快速安装

```bash
git clone <你的仓库地址>
cd music-agent
./scripts/install_hermes_skill.sh
```

这个脚本会做两件事：

- 把 Hermes skill 安装到 `~/.hermes/skills/media/music`
- 把 `musicctl` 包装脚本安装到 `~/.local/bin/musicctl`

请确认 `~/.local/bin` 已经在你的 `PATH` 中。

### 作为 Python 包安装

如果你希望通过用户目录安装 Python 包，可以执行：

```bash
python3 -m pip install --user .
```

## Hermes 使用方式

安装完 skill 之后，可以直接在 Hermes 中使用：

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
musicctl --text play "稻香"
```

### 热榜播放

```bash
musicctl --text hot
musicctl --text hot english
musicctl --text lang japanese
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

### 音量控制

```bash
musicctl --text volume 60
musicctl --text volume up
musicctl --text volume down
musicctl --text mute
musicctl --text unmute
```

## 命令总表

| 命令 | 说明 |
|---|---|
| `musicctl --text play "<关键词>"` | 按关键词生成队列并开始播放 |
| `musicctl --text hot [lang]` | 按当前或临时指定语种播放 KKBOX 周榜热歌 |
| `musicctl --text lang [lang]` | 查看或设置当前会话热榜语种 |
| `musicctl --text pause` | 暂停播放 |
| `musicctl --text resume` | 恢复播放 |
| `musicctl --text next` | 下一首 |
| `musicctl --text prev` | 上一首 |
| `musicctl --text stop` | 停止播放并清空活动队列 |
| `musicctl --text status` | 查看当前状态 |
| `musicctl --text volume <0-100>` | 设置音量 |
| `musicctl --text volume up` | 音量增加 5 |
| `musicctl --text volume down` | 音量减少 5 |
| `musicctl --text mute` | 静音 |
| `musicctl --text unmute` | 恢复到上一次非 0 音量 |

## 仓库结构

```text
music-agent/
├── musicctl/
├── musicd/
├── shared/
├── skills/
├── tests/
├── scripts/
├── README.md
└── README.zh-CN.md
```

## 当前限制

- 必须安装本地 `mpv` 才能真正播放
- 搜索质量依赖上游平台返回结果
- Bilibili 的搜索结果天然较杂，后续还需要继续加强过滤
- 项目不会下载和管理本地音乐库
- 项目不提供 GUI

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

- 继续优化关键词排序，优先原唱和官方版本
- 加强音源过滤和去重
- 增加 daemon IPC 与播放器行为的更多集成测试
- 提供更完整的 OpenClaw 打包方式

## 许可证

在发布到 GitHub 前，请补充你希望采用的开源许可证。


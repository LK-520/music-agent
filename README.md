# music-agent

[中文说明](./README.zh-CN.md)

`music-agent` is a local background music controller for Hermes and OpenClaw.
It lets you play network music from the terminal without opening a browser,
without opening an extra window, and without saving audio files to disk.

## Highlights

- Local background playback powered by `mpv`
- One command surface for playback, queue, volume, mute, and status
- Source priority: `YouTube -> Bilibili -> SoundCloud`
- Keyword-based queues with up to 20 tracks
- KKBOX weekly hot charts for:
  `mandarin`, `english`, `japanese`, `korean`, `cantonese`
- Works well with Hermes `/music ...` skill usage

## Status

The current codebase has passing local unit tests:

```bash
python3 -m unittest discover -s tests -v
```

End-to-end playback still depends on local runtime tools being installed:

- `mpv`
- `python3 -m yt_dlp`

If `mpv` is missing, playback commands fail fast with a clear error message.

## Demo Commands

```bash
musicctl --text play "Jay Chou"
musicctl --text play "周杰伦 稻香"
musicctl --text hot
musicctl --text hot english
musicctl --text lang cantonese
musicctl --text status
musicctl --text pause
musicctl --text resume
musicctl --text next
musicctl --text prev
musicctl --text volume 60
musicctl --text volume up
musicctl --text mute
```

## Features

### Playback

- Start a new queue from a keyword
- Start a hot chart queue from KKBOX weekly charts
- Replace the current queue when a new `play` or `hot` command succeeds
- Loop playback by default
- Skip failed tracks automatically

### Control

- Pause / resume
- Next / previous
- Stop
- Status query
- Volume set / up / down
- Mute / unmute

### Language Preference

Hot chart mode supports a session-level language preference:

- `mandarin`
- `english`
- `japanese`
- `korean`
- `cantonese`

Accepted aliases include both Chinese and simple English forms.
Examples:

- `华语`, `中文`, `mandarin`, `cn`
- `英语`, `english`, `en`
- `日语`, `japanese`, `jp`
- `韩语`, `korean`, `kr`
- `粤语`, `cantonese`, `yue`

## Architecture

```text
/music ...
  -> skill layer
  -> musicctl
  -> musicd
  -> source adapters
  -> mpv
```

### Components

- `musicctl`: short-lived CLI client
- `musicd`: local background daemon
- `shared`: models, language mapping, runtime paths, helpers
- `skills/hermes/music`: Hermes skill definition
- `skills/openclaw/music`: OpenClaw-oriented skill definition

## Requirements

- Python 3.9+
- `mpv`
- `python3 -m yt_dlp`
- macOS or another environment that supports Unix domain sockets and `mpv`

## Installation

### Quick Install for Hermes Users

```bash
git clone <your-repo-url>
cd music-agent
./scripts/install_hermes_skill.sh
```

This installs:

- Hermes skill to `~/.hermes/skills/media/music`
- `musicctl` wrapper to `~/.local/bin/musicctl`

Make sure `~/.local/bin` is in your `PATH`.

### Python Package Install

If you want the Python package available in your user site:

```bash
python3 -m pip install --user .
```

## Hermes Usage

After installing the skill, you can use commands such as:

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

## CLI Usage

### Play from Keyword

```bash
musicctl --text play "周杰伦"
musicctl --text play "稻香"
```

### Hot Charts

```bash
musicctl --text hot
musicctl --text hot english
musicctl --text lang japanese
musicctl --text hot
```

### Playback Control

```bash
musicctl --text pause
musicctl --text resume
musicctl --text next
musicctl --text prev
musicctl --text stop
musicctl --text status
```

### Volume

```bash
musicctl --text volume 60
musicctl --text volume up
musicctl --text volume down
musicctl --text mute
musicctl --text unmute
```

## Command Reference

| Command | Description |
|---|---|
| `musicctl --text play "<query>"` | Build a keyword queue and start playback |
| `musicctl --text hot [lang]` | Play KKBOX weekly hot chart for the current or provided language |
| `musicctl --text lang [lang]` | Show or set the session hot-chart language |
| `musicctl --text pause` | Pause playback |
| `musicctl --text resume` | Resume playback |
| `musicctl --text next` | Skip to next track |
| `musicctl --text prev` | Go to previous track |
| `musicctl --text stop` | Stop playback and clear active queue |
| `musicctl --text status` | Show current state |
| `musicctl --text volume <0-100>` | Set volume |
| `musicctl --text volume up` | Increase volume by 5 |
| `musicctl --text volume down` | Decrease volume by 5 |
| `musicctl --text mute` | Mute playback |
| `musicctl --text unmute` | Restore previous non-zero volume |

## Project Layout

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

## Limitations

- Playback requires a working local `mpv` installation
- Search quality depends on upstream source results
- Some Bilibili results are noisy and may still require future filtering improvements
- This project does not download and manage a local music library
- This project does not provide a GUI

## Development

### Run Tests

```bash
python3 -m unittest discover -s tests -v
```

### Basic Smoke Checks

```bash
musicctl --text status
musicctl --text lang english
musicctl --text hot english
```

## Roadmap

- Better keyword ranking for original/official versions
- Stronger source filtering and de-duplication
- More integration coverage around daemon IPC and player behavior
- Better OpenClaw packaging story

## License

Add your preferred open source license before publishing to GitHub.

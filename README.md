<p align="center">
  <img src="./assets/music-agent-mark.svg" alt="music-agent logo" width="240">
</p>

<h1 align="center">music-agent</h1>

<p align="center">
  Local background music control for Hermes and OpenClaw.
</p>

<p align="center">
  No browser. No extra window. No local audio files.
</p>

<p align="center">
  <a href="./README.zh-CN.md">中文说明</a>
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

## Overview

`music-agent` is a local background music controller built for terminal-first workflows.
It is designed for Hermes and OpenClaw users who want a simple `/music ...` experience
with local playback, clear CLI feedback, and a source pipeline that stays out of the way.

## Why It Exists

- Play network music from the terminal
- Keep playback local and in the background
- Avoid browser tabs and popup players
- Avoid storing downloaded audio files on disk
- Provide a clean bridge between slash-command UX and real local playback

## Core Capabilities

- Local background playback powered by `mpv`
- Keyword-driven queues with up to 20 tracks
- KKBOX weekly hot chart playback
- Hot-chart language preference for:
  `mandarin`, `english`, `japanese`, `korean`, `cantonese`
- Source priority:
  `YouTube -> Bilibili -> SoundCloud`
- Pause, resume, next, previous, stop, status, volume, mute, and unmute
- Hermes-friendly `/music ...` skill workflow

## Current Status

Local unit tests are passing:

```bash
python3 -m unittest discover -s tests -v
```

Runtime playback still depends on local tools being available:

- `mpv`
- `python3 -m yt_dlp`

If `mpv` is not installed, playback commands fail fast with a clear message.

## Screenshot Style README Header

This repository includes:

- a centered project mark for GitHub presentation
- a badge row for quick scanning
- English and Chinese README entry points

The main visual asset lives here:

- [`assets/music-agent-mark.svg`](./assets/music-agent-mark.svg)

## Quick Start

```bash
git clone git@github.com:LK-520/music-agent.git
cd music-agent
./scripts/install_hermes_skill.sh
musicctl --text status
```

The install script does two things:

- installs the Hermes skill into `~/.hermes/skills/media/music`
- installs a `musicctl` wrapper into `~/.local/bin/musicctl`

Make sure `~/.local/bin` is available in your `PATH`.

## Requirements

- Python 3.9+
- `mpv`
- `python3 -m yt_dlp`
- An environment that supports Unix domain sockets and local `mpv` control

## Hermes Usage

After installing the skill, you can use commands like:

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

### Keyword Playback

```bash
musicctl --text play "周杰伦"
musicctl --text play "周杰伦 稻香"
musicctl --text play "Jay Chou"
```

### Hot Charts

```bash
musicctl --text hot
musicctl --text hot english
musicctl --text hot japanese
musicctl --text lang cantonese
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

### Volume and Mute

```bash
musicctl --text volume 60
musicctl --text volume up
musicctl --text volume down
musicctl --text mute
musicctl --text unmute
```

## Supported Hot Languages

The hot-chart feature maps user-friendly aliases to internal language keys:

| Internal key | Common aliases |
|---|---|
| `mandarin` | `华语`, `中文`, `汉语`, `mandarin`, `cn` |
| `english` | `英语`, `英文`, `english`, `en` |
| `japanese` | `日语`, `日文`, `japanese`, `jp` |
| `korean` | `韩语`, `韩文`, `korean`, `kr` |
| `cantonese` | `粤语`, `cantonese`, `yue`, `hk` |

## Architecture

```text
/music ...
  -> skill layer
  -> musicctl
  -> musicd
  -> source adapters
  -> mpv
```

### Main Modules

- `musicctl`
  CLI entry point and response formatter
- `musicd`
  local daemon, queue manager, player coordinator
- `shared`
  common models, runtime paths, language mapping, and helpers
- `skills/hermes/music`
  Hermes skill definition
- `skills/openclaw/music`
  OpenClaw-oriented skill definition

## Project Layout

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

## Limitations

- Playback requires a working local `mpv` installation
- Search quality depends on upstream source availability and result quality
- Bilibili results are noisier than YouTube and still need future filtering improvements
- This project does not build a local music library
- This project does not provide a GUI

## Disclaimer

- `music-agent` is a local control tool and does not provide any music catalog, account service, or hosted streaming service.
- Playback availability depends on third-party platforms such as YouTube, Bilibili, SoundCloud, and KKBOX. Upstream changes, regional restrictions, takedowns, or API behavior changes may affect results at any time.
- Users are responsible for complying with the terms of service, copyright rules, and local laws that apply to the music sources they access through this project.
- This project is intended for personal, lawful use. Do not use it to redistribute copyrighted audio, bypass platform restrictions, or build unlicensed commercial music services.
- The maintainers of this repository do not own the copyrights to third-party audio, artwork, charts, or metadata referenced by external sources.

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

- Better keyword ranking toward official and original versions
- Stronger source filtering and de-duplication
- More daemon/player integration coverage
- Cleaner OpenClaw packaging and setup docs

## License

This project is licensed under the [MIT License](./LICENSE).

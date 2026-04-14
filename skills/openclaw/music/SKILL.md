---
name: music
description: 在本机后台播放网络音乐并控制播放状态。适用于 /music ... 命令。
---

# Music

当用户调用 `/music ...` 时，执行本地 `musicctl --text ...` 命令完成音乐控制。

命令映射：

- `/music keyword 周杰伦` -> `musicctl --text play "周杰伦"`
- `/music hot` -> `musicctl --text hot`
- `/music hot english` -> `musicctl --text hot english`
- `/music pause` -> `musicctl --text pause`
- `/music resume` -> `musicctl --text resume`
- `/music next` -> `musicctl --text next`
- `/music prev` -> `musicctl --text prev`
- `/music stop` -> `musicctl --text stop`
- `/music status` -> `musicctl --text status`
- `/music volume 60` -> `musicctl --text volume 60`
- `/music volume up` -> `musicctl --text volume up`
- `/music volume down` -> `musicctl --text volume down`
- `/music mute` -> `musicctl --text mute`
- `/music unmute` -> `musicctl --text unmute`
- `/music lang` -> `musicctl --text lang`
- `/music lang 粤语` -> `musicctl --text lang 粤语`

直接返回命令输出，不打开浏览器，不弹窗。


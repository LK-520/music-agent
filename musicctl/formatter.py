from __future__ import annotations

from shared.lang import display_lang


def format_response(response: dict) -> str:
    if not response.get("ok"):
        return response.get("message") or "请求失败"
    action = response.get("action")
    if action == "play":
        track = response.get("track") or {}
        return f"已开始播放“{response.get('query', '')}”相关队列，共 {response.get('queue_total', 0)} 首，当前：{track.get('artist', '未知歌手')} - {track.get('title', '未知歌曲')}"
    if action == "hot":
        track = response.get("track") or {}
        lang = response.get("lang")
        return f"已开始播放{display_lang(lang)}热门歌曲队列，共 {response.get('queue_total', 0)} 首，当前：{track.get('artist', '未知歌手')} - {track.get('title', '未知歌曲')}"
    if action == "pause":
        return "已暂停播放"
    if action == "resume":
        track = response.get("track") or {}
        return f"已继续播放：{track.get('artist', '未知歌手')} - {track.get('title', '未知歌曲')}"
    if action == "next":
        track = response.get("track") or {}
        return f"已切换到下一首：{track.get('artist', '未知歌手')} - {track.get('title', '未知歌曲')}"
    if action == "prev":
        track = response.get("track") or {}
        return f"已切换到上一首：{track.get('artist', '未知歌手')} - {track.get('title', '未知歌曲')}"
    if action == "stop":
        return "已停止播放"
    if action == "status":
        if response.get("state") == "idle":
            return f"当前没有正在播放的音乐｜语种偏好：{display_lang(response.get('lang', 'mandarin'))}"
        if response.get("state") == "error":
            return response.get("message") or "音乐服务异常"
        track = response.get("track") or {}
        state_map = {"playing": "播放中", "paused": "已暂停"}
        queue_index = response.get("queue_index") or "-"
        queue_total = response.get("queue_total") or "-"
        muted = "是" if response.get("muted") else "否"
        return (
            f"当前播放：{track.get('artist', '未知歌手')} - {track.get('title', '未知歌曲')}"
            f"｜状态：{state_map.get(response.get('state'), response.get('state'))}"
            f"｜音量：{response.get('volume', 0)}"
            f"｜静音：{muted}"
            f"｜队列：{queue_index}/{queue_total}"
            f"｜模式：循环"
            f"｜来源：{track.get('source', 'unknown')}"
            f"｜热榜语种：{display_lang(response.get('lang', 'mandarin'))}"
        )
    if action == "volume":
        return f"音量已设置为 {response.get('volume', 0)}"
    if action == "mute":
        return "已静音"
    if action == "unmute":
        return f"已取消静音，当前音量：{response.get('volume', 0)}"
    if action == "lang":
        return f"当前热榜语种：{response.get('display')}"
    return "操作成功"


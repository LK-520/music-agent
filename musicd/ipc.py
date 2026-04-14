from __future__ import annotations

import json
import socket
from typing import Any, Dict

from shared.runtime import SOCKET_PATH
from shared.utils import json_dumps, recv_json_line


def send_request(payload: Dict[str, Any]) -> dict:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(20)
        client.connect(str(SOCKET_PATH))
        client.sendall(json_dumps(payload))
        return recv_json_line(client)


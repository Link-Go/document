from typing import Dict
from fastapi import WebSocket

CONNECTIONS: Dict[str, WebSocket] = {}  # websocket connections
WS_TIMEOUT = 1  # second

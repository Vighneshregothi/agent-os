from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


class AuditLogger:
    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: Dict[str, Any]) -> None:
        flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
        fd = os.open(self.log_path, flags, 0o644)
        try:
            serialized = json.dumps(event, sort_keys=True)
            os.write(fd, (serialized + "\n").encode("utf-8"))
            os.fsync(fd)
        finally:
            os.close(fd)

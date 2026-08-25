import json
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.config import settings

class MemoryStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._rules: List[Dict[str, Any]] = []
        self._devices: Dict[str, Any] = {}
        self._load_devices()

    def _load_devices(self):
        devices_file = settings.DEVICES_FILE
        if devices_file.exists():
            with open(devices_file, "r", encoding="utf-8") as f:
                self._devices = json.load(f)
        else:
            self._devices = {}

    def get_devices(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._devices)

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._devices.get(device_id)

    def add_rule(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            rule_id = f"rule-{uuid.uuid4().hex[:8]}"
            rule = {
                "id": rule_id,
                "device_id": action_data.get("device_id"),
                "metric": action_data.get("metric"),
                "condition": str(action_data.get("condition")),
                "threshold": float(action_data.get("threshold")),
                "duration_minutes": int(action_data.get("duration_minutes")),
                "notify_via": [str(c) for c in action_data.get("notify_via", ["EMAIL"])],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            self._rules.append(rule)
            return rule

    def get_rules(self, device_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            if device_id:
                return [r for r in self._rules if r.get("device_id") == device_id]
            return list(self._rules)

    def get_telemetry(self, device_id: str, metric: str) -> Optional[Any]:
        with self._lock:
            device = self._devices.get(device_id)
            if not device:
                return None
            telemetry = device.get("telemetry", {})
            return telemetry.get(metric)

    def reset(self):
        with self._lock:
            self._rules.clear()
            self._load_devices()

# Singleton instance
memory_store = MemoryStore()

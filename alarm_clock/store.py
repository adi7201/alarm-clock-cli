"""JSON-backed persistence for alarms.

Kept deliberately simple: every operation reads the whole file, mutates
in memory, and writes it back. Alarm counts for a personal CLI tool are
small (dozens, not millions), so this trades a bit of I/O for code that's
trivial to reason about and to test.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import Alarm

DEFAULT_PATH = Path.home() / ".alarm_clock" / "alarms.json"


class AlarmStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else DEFAULT_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> List[Alarm]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return [Alarm.from_dict(d) for d in raw]

    def _save(self, alarms: List[Alarm]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump([a.to_dict() for a in alarms], f, indent=2)

    def list(self, include_disabled: bool = True) -> List[Alarm]:
        alarms = self._load()
        if include_disabled:
            return alarms
        return [a for a in alarms if a.enabled]

    def add(self, alarm: Alarm) -> Alarm:
        alarms = self._load()
        alarms.append(alarm)
        self._save(alarms)
        return alarm

    def get(self, alarm_id: str) -> Alarm:
        for alarm in self._load():
            if alarm.id == alarm_id:
                return alarm
        raise KeyError(alarm_id)

    def remove(self, alarm_id: str) -> None:
        alarms = self._load()
        remaining = [a for a in alarms if a.id != alarm_id]
        if len(remaining) == len(alarms):
            raise KeyError(alarm_id)
        self._save(remaining)

    def set_enabled(self, alarm_id: str, enabled: bool) -> None:
        alarms = self._load()
        found = False
        for alarm in alarms:
            if alarm.id == alarm_id:
                alarm.enabled = enabled
                found = True
        if not found:
            raise KeyError(alarm_id)
        self._save(alarms)

    def due_alarms(self, now: datetime) -> List[Alarm]:
        return [a for a in self._load() if a.is_due(now)]

    def mark_triggered(self, alarm_id: str, now: datetime) -> None:
        alarms = self._load()
        for alarm in alarms:
            if alarm.id == alarm_id:
                alarm.last_triggered = now.strftime("%Y-%m-%d %H:%M")
                if alarm.repeat == "once":
                    alarm.enabled = False
        self._save(alarms)

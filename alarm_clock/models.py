"""Alarm data model and due-check logic."""
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional
import uuid

# Canonical weekday order, used both for validation and for display.
VALID_DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


@dataclass
class Alarm:
    id: str
    time: str  # "HH:MM", 24-hour
    label: str = ""
    repeat: str = "once"  # "once" | "daily" | "mon,wed,fri"
    enabled: bool = True
    last_triggered: Optional[str] = None  # "YYYY-MM-DD HH:MM", set after firing

    @staticmethod
    def new(time: str, label: str = "", repeat: str = "once") -> "Alarm":
        return Alarm(id=uuid.uuid4().hex[:8], time=time, label=label, repeat=repeat)

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Alarm":
        return Alarm(**data)

    def is_due(self, now: datetime) -> bool:
        """True if this alarm should fire at `now` (minute resolution)."""
        if not self.enabled:
            return False
        if now.strftime("%H:%M") != self.time:
            return False

        # Guard against firing more than once within the same minute,
        # since the run loop polls sub-minute.
        minute_key = now.strftime("%Y-%m-%d %H:%M")
        if self.last_triggered == minute_key:
            return False

        if self.repeat in ("once", "daily"):
            return True

        today = now.strftime("%a").lower()[:3]
        return today in self.repeat.split(",")

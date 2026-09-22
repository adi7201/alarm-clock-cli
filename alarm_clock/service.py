import json
from pathlib import Path

from .models import Alarm, validate_time

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "alarm.json"


def _load(path: Path = DATA_FILE) -> dict:
    if not path.exists():
        return {"next_id": 1, "alarms": []}
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return {
        "next_id": raw.get("next_id", 1),
        "alarms": [Alarm.from_dict(a) for a in raw.get("alarms", [])],
    }


def _save(state: dict, path: Path = DATA_FILE) -> None:
    # No file locking: concurrent CLI invocations against the same file are
    # not protected against races. Acceptable for single-user sequential use.
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = {
        "next_id": state["next_id"],
        "alarms": [a.to_dict() for a in state["alarms"]],
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2)


def add_alarm(time_str: str, label: str = "", path: Path = DATA_FILE) -> Alarm:
    validate_time(time_str)
    state = _load(path)
    alarm = Alarm(id=state["next_id"], time=time_str, label=label, enabled=True)
    state["alarms"].append(alarm)
    state["next_id"] += 1
    _save(state, path)
    return alarm


def list_alarms(path: Path = DATA_FILE) -> list:
    state = _load(path)
    return sorted(state["alarms"], key=lambda a: a.time)


def delete_alarm(alarm_id: int, path: Path = DATA_FILE) -> None:
    state = _load(path)
    remaining = [a for a in state["alarms"] if a.id != alarm_id]
    if len(remaining) == len(state["alarms"]):
        raise LookupError(f"no alarm with id {alarm_id}")
    state["alarms"] = remaining
    _save(state, path)


def set_enabled(alarm_id: int, enabled: bool, path: Path = DATA_FILE) -> Alarm:
    state = _load(path)
    for alarm in state["alarms"]:
        if alarm.id == alarm_id:
            alarm.enabled = enabled
            _save(state, path)
            return alarm
    raise LookupError(f"no alarm with id {alarm_id}")


def get_due_alarms(now_hhmm: str, path: Path = DATA_FILE) -> list:
    state = _load(path)
    return [a for a in state["alarms"] if a.enabled and a.time == now_hhmm]

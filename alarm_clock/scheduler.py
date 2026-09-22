import time
from datetime import datetime
from pathlib import Path

from . import service, trigger
from .service import DATA_FILE


def tick(now_hhmm: str, path: Path = DATA_FILE) -> list:
    due = service.get_due_alarms(now_hhmm, path=path)
    for alarm in due:
        trigger.notify(alarm)
        service.delete_alarm(alarm.id, path=path)
    return due


def run_forever(poll_interval: float = 1.0, path: Path = DATA_FILE) -> None:
    print("Alarm scheduler running. Press Ctrl+C to stop.")
    try:
        while True:
            tick(datetime.now().strftime("%H:%M"), path=path)
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("\nScheduler stopped.")

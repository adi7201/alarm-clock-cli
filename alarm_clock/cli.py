"""Command-line interface for the alarm clock."""
import argparse
import re
import sys
import threading
import time
from datetime import datetime, timedelta
from typing import List

from .models import Alarm, VALID_DAYS
from .sound import play_sound
from .store import AlarmStore

TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def valid_time(value: str) -> str:
    if not TIME_RE.match(value):
        raise argparse.ArgumentTypeError(
            f"invalid time '{value}': use 24-hour HH:MM, e.g. 07:30"
        )
    return value


def valid_repeat(value: str) -> str:
    value = value.strip().lower()
    if value in ("once", "daily"):
        return value
    days = value.split(",")
    for day in days:
        if day not in VALID_DAYS:
            raise argparse.ArgumentTypeError(
                f"invalid repeat '{value}': use 'once', 'daily', or comma-separated "
                f"days from {VALID_DAYS}"
            )
    # De-duplicate and store in canonical (mon..sun) order.
    ordered = [d for d in VALID_DAYS if d in days]
    return ",".join(ordered)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="alarm", description="A simple terminal alarm clock."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="add a new alarm")
    p_add.add_argument("time", type=valid_time, help="time in 24h HH:MM format")
    p_add.add_argument("--label", default="", help="optional label, e.g. 'Standup'")
    p_add.add_argument(
        "--repeat",
        type=valid_repeat,
        default="once",
        help="'once' (default), 'daily', or comma-separated days (mon,tue,...)",
    )

    p_list = sub.add_parser("list", help="list alarms")
    p_list.add_argument(
        "--all", action="store_true", help="include disabled/used-up alarms"
    )

    p_remove = sub.add_parser("remove", help="remove an alarm by id")
    p_remove.add_argument("id")

    p_enable = sub.add_parser("enable", help="enable an alarm by id")
    p_enable.add_argument("id")

    p_disable = sub.add_parser("disable", help="disable an alarm by id")
    p_disable.add_argument("id")

    p_run = sub.add_parser("run", help="watch for due alarms (foreground)")
    p_run.add_argument(
        "--interval", type=float, default=1.0, help="polling interval, in seconds"
    )
    p_run.add_argument(
        "--snooze", type=int, default=5, help="snooze duration, in minutes"
    )

    return parser


def print_alarms(alarms: List[Alarm]) -> None:
    if not alarms:
        print("No alarms.")
        return
    rows = [("ID", "TIME", "REPEAT", "STATUS", "LABEL")]
    for a in alarms:
        status = "on" if a.enabled else "off"
        rows.append((a.id, a.time, a.repeat, status, a.label))
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    for row in rows:
        print("  ".join(cell.ljust(w) for cell, w in zip(row, widths)))


def ring(alarm: Alarm, store: AlarmStore, now: datetime, snooze_minutes: int) -> None:
    """Beep until the user dismisses or snoozes the alarm."""
    stop_event = threading.Event()

    def beeper():
        while not stop_event.is_set():
            play_sound()
            stop_event.wait(1.0)

    beeper_thread = threading.Thread(target=beeper, daemon=True)
    beeper_thread.start()

    label = f" - {alarm.label}" if alarm.label else ""
    print(f"\nALARM! {alarm.time}{label}")
    try:
        choice = input("Press Enter to dismiss, or 's' + Enter to snooze: ").strip().lower()
    finally:
        stop_event.set()
        beeper_thread.join()

    if choice == "s":
        snooze_time = (now + timedelta(minutes=snooze_minutes)).strftime("%H:%M")
        snoozed = Alarm.new(snooze_time, label=alarm.label, repeat="once")
        store.add(snoozed)
        print(f"Snoozed until {snooze_time} (id {snoozed.id})")


def run_loop(store: AlarmStore, interval: float, snooze_minutes: int) -> None:
    print("Alarm clock running. Press Ctrl+C to stop.")
    try:
        while True:
            now = datetime.now()
            for alarm in store.due_alarms(now):
                # Mark triggered before ringing so a slow/blocked ring()
                # can't cause the same alarm to fire twice.
                store.mark_triggered(alarm.id, now)
                ring(alarm, store, now, snooze_minutes)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped.")


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = AlarmStore()

    if args.command == "add":
        alarm = Alarm.new(args.time, args.label, args.repeat)
        store.add(alarm)
        suffix = f" - {alarm.label}" if alarm.label else ""
        print(f"Added alarm {alarm.id}: {alarm.time} ({alarm.repeat}){suffix}")
        return 0

    if args.command == "list":
        print_alarms(store.list(include_disabled=args.all))
        return 0

    if args.command == "remove":
        try:
            store.remove(args.id)
        except KeyError:
            print(f"No alarm with id '{args.id}'", file=sys.stderr)
            return 1
        print(f"Removed alarm {args.id}")
        return 0

    if args.command in ("enable", "disable"):
        try:
            store.set_enabled(args.id, args.command == "enable")
        except KeyError:
            print(f"No alarm with id '{args.id}'", file=sys.stderr)
            return 1
        print(f"{'Enabled' if args.command == 'enable' else 'Disabled'} alarm {args.id}")
        return 0

    if args.command == "run":
        run_loop(store, interval=args.interval, snooze_minutes=args.snooze)
        return 0

    parser.error(f"unknown command '{args.command}'")
    return 2


if __name__ == "__main__":
    sys.exit(main())

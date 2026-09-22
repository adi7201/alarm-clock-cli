import argparse
import sys
from datetime import datetime

from . import scheduler, service


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="alarm", description="A simple terminal alarm clock.")
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Add a new alarm")
    add_p.add_argument("time", help="Alarm time in 24-hour HH:MM format")
    add_p.add_argument("--label", default="", help="Optional label for the alarm")

    sub.add_parser("list", help="List all alarms")

    delete_p = sub.add_parser("delete", help="Delete an alarm")
    delete_p.add_argument("id", type=int, help="Alarm id")

    enable_p = sub.add_parser("enable", help="Enable an alarm")
    enable_p.add_argument("id", type=int, help="Alarm id")

    disable_p = sub.add_parser("disable", help="Disable an alarm")
    disable_p.add_argument("id", type=int, help="Alarm id")

    run_p = sub.add_parser("run", help="Start the alarm scheduler (blocks until Ctrl+C)")
    run_p.add_argument("--interval", type=float, default=1.0, help="Poll interval in seconds")

    return parser


def _cmd_add(args) -> int:
    try:
        alarm = service.add_alarm(args.time, label=args.label)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(f"Added alarm {alarm.id}: {alarm.time} ({alarm.label or 'no label'})")
    return 0


def _cmd_list(args) -> int:
    alarms = service.list_alarms()
    if not alarms:
        print("No alarms.")
        return 0
    now_hhmm = datetime.now().strftime("%H:%M")
    print(f"{'ID':<4}{'TIME':<8}{'WHEN':<10}{'ENABLED':<10}LABEL")
    for a in alarms:
        when = "today" if a.time > now_hhmm else "tomorrow"
        print(f"{a.id:<4}{a.time:<8}{when:<10}{str(a.enabled):<10}{a.label}")
    return 0


def _cmd_delete(args) -> int:
    try:
        service.delete_alarm(args.id)
    except LookupError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(f"Deleted alarm {args.id}")
    return 0


def _cmd_set_enabled(args, enabled: bool) -> int:
    try:
        service.set_enabled(args.id, enabled)
    except LookupError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(f"{'Enabled' if enabled else 'Disabled'} alarm {args.id}")
    return 0


def _cmd_run(args) -> int:
    scheduler.run_forever(poll_interval=args.interval)
    return 0


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "add":
        return _cmd_add(args)
    if args.command == "list":
        return _cmd_list(args)
    if args.command == "delete":
        return _cmd_delete(args)
    if args.command == "enable":
        return _cmd_set_enabled(args, True)
    if args.command == "disable":
        return _cmd_set_enabled(args, False)
    if args.command == "run":
        return _cmd_run(args)

    parser.print_help()
    return 1

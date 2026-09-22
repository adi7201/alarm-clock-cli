from .models import Alarm


def notify(alarm: Alarm) -> None:
    banner = (
        "\n" + "=" * 42 + "\n"
        f"  ALARM: {alarm.label or '(no label)'}\n"
        f"  TIME:  {alarm.time}\n"
        + "=" * 42 + "\n"
    )
    print("\a" * 3 + banner, flush=True)

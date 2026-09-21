from datetime import datetime

from alarm_clock.models import Alarm


def test_once_alarm_due_at_exact_minute():
    alarm = Alarm.new("07:30", repeat="once")
    now = datetime(2026, 9, 21, 7, 30, 5)
    assert alarm.is_due(now)


def test_alarm_not_due_at_other_times():
    alarm = Alarm.new("07:30", repeat="once")
    now = datetime(2026, 9, 21, 7, 31, 0)
    assert not alarm.is_due(now)


def test_disabled_alarm_never_due():
    alarm = Alarm.new("07:30", repeat="daily")
    alarm.enabled = False
    now = datetime(2026, 9, 21, 7, 30, 0)
    assert not alarm.is_due(now)


def test_daily_alarm_fires_every_day():
    alarm = Alarm.new("07:30", repeat="daily")
    assert alarm.is_due(datetime(2026, 9, 21, 7, 30))  # Monday
    assert alarm.is_due(datetime(2026, 9, 27, 7, 30))  # Sunday


def test_weekday_alarm_only_fires_on_selected_days():
    # 2026-09-21 is a Monday, 2026-09-22 is a Tuesday.
    alarm = Alarm.new("07:30", repeat="mon,wed,fri")
    assert alarm.is_due(datetime(2026, 9, 21, 7, 30))
    assert not alarm.is_due(datetime(2026, 9, 22, 7, 30))


def test_alarm_does_not_refire_within_same_minute():
    alarm = Alarm.new("07:30", repeat="daily")
    now = datetime(2026, 9, 21, 7, 30, 0)
    alarm.last_triggered = now.strftime("%Y-%m-%d %H:%M")
    assert not alarm.is_due(now)


def test_round_trip_to_dict_and_back():
    alarm = Alarm.new("07:30", label="Standup", repeat="daily")
    restored = Alarm.from_dict(alarm.to_dict())
    assert restored == alarm

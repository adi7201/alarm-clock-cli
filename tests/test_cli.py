from datetime import datetime
from unittest.mock import patch

from alarm_clock.cli import ring
from alarm_clock.models import Alarm
from alarm_clock.store import AlarmStore


@patch("alarm_clock.cli.play_sound")
def test_dismiss_does_not_create_snoozed_alarm(mock_sound, tmp_path):
    store = AlarmStore(path=tmp_path / "alarms.json")
    alarm = Alarm.new("07:30", repeat="once")
    store.add(alarm)

    with patch("builtins.input", return_value=""):
        ring(alarm, store, datetime(2026, 9, 21, 7, 30), snooze_minutes=5)

    assert len(store.list()) == 1  # only the original alarm
    assert mock_sound.called


@patch("alarm_clock.cli.play_sound")
def test_snooze_creates_new_alarm_offset_by_snooze_minutes(mock_sound, tmp_path):
    store = AlarmStore(path=tmp_path / "alarms.json")
    alarm = Alarm.new("07:30", repeat="once")
    store.add(alarm)

    with patch("builtins.input", return_value="s"):
        ring(alarm, store, datetime(2026, 9, 21, 7, 30), snooze_minutes=5)

    alarms = store.list()
    assert len(alarms) == 2
    snoozed = [a for a in alarms if a.id != alarm.id][0]
    assert snoozed.time == "07:35"
    assert snoozed.repeat == "once"

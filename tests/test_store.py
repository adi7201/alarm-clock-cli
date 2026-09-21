from datetime import datetime

import pytest

from alarm_clock.models import Alarm
from alarm_clock.store import AlarmStore


@pytest.fixture
def store(tmp_path):
    return AlarmStore(path=tmp_path / "alarms.json")


def test_add_and_list(store):
    alarm = Alarm.new("07:30", label="Wake up")
    store.add(alarm)
    listed = store.list()
    assert len(listed) == 1
    assert listed[0].id == alarm.id
    assert listed[0].label == "Wake up"


def test_persists_across_instances(tmp_path):
    path = tmp_path / "alarms.json"
    store_a = AlarmStore(path=path)
    store_a.add(Alarm.new("07:30"))

    store_b = AlarmStore(path=path)
    assert len(store_b.list()) == 1


def test_remove(store):
    alarm = Alarm.new("07:30")
    store.add(alarm)
    store.remove(alarm.id)
    assert store.list() == []


def test_remove_missing_raises(store):
    with pytest.raises(KeyError):
        store.remove("nonexistent")


def test_set_enabled(store):
    alarm = Alarm.new("07:30")
    store.add(alarm)
    store.set_enabled(alarm.id, False)
    assert store.get(alarm.id).enabled is False


def test_list_excludes_disabled_when_requested(store):
    a = Alarm.new("07:30")
    store.add(a)
    store.set_enabled(a.id, False)
    assert store.list(include_disabled=False) == []
    assert len(store.list(include_disabled=True)) == 1


def test_due_alarms_filters_by_time(store):
    store.add(Alarm.new("07:30", repeat="daily"))
    store.add(Alarm.new("08:00", repeat="daily"))
    due = store.due_alarms(datetime(2026, 9, 21, 7, 30))
    assert len(due) == 1
    assert due[0].time == "07:30"


def test_mark_triggered_disables_once_off_alarm(store):
    alarm = Alarm.new("07:30", repeat="once")
    store.add(alarm)
    now = datetime(2026, 9, 21, 7, 30)
    store.mark_triggered(alarm.id, now)
    updated = store.get(alarm.id)
    assert updated.enabled is False
    assert updated.last_triggered == "2026-09-21 07:30"


def test_mark_triggered_keeps_daily_alarm_enabled(store):
    alarm = Alarm.new("07:30", repeat="daily")
    store.add(alarm)
    now = datetime(2026, 9, 21, 7, 30)
    store.mark_triggered(alarm.id, now)
    assert store.get(alarm.id).enabled is True

import pytest

from alarm_clock import service


@pytest.fixture
def data_path(tmp_path):
    return tmp_path / "alarm.json"


def test_add_alarm_valid(data_path):
    alarm = service.add_alarm("07:30", label="Wake up", path=data_path)
    assert alarm.id == 1
    assert alarm.time == "07:30"
    assert alarm.label == "Wake up"
    assert alarm.enabled is True


def test_add_alarm_invalid_time(data_path):
    with pytest.raises(ValueError):
        service.add_alarm("25:99", path=data_path)
    with pytest.raises(ValueError):
        service.add_alarm("7:3", path=data_path)


def test_list_alarms_sorted_by_time(data_path):
    service.add_alarm("15:00", path=data_path)
    service.add_alarm("07:30", path=data_path)
    service.add_alarm("12:00", path=data_path)
    times = [a.time for a in service.list_alarms(path=data_path)]
    assert times == ["07:30", "12:00", "15:00"]


def test_delete_alarm(data_path):
    alarm = service.add_alarm("07:30", path=data_path)
    service.delete_alarm(alarm.id, path=data_path)
    assert service.list_alarms(path=data_path) == []


def test_delete_missing_alarm_raises(data_path):
    with pytest.raises(LookupError):
        service.delete_alarm(999, path=data_path)


def test_set_enabled_toggles(data_path):
    alarm = service.add_alarm("07:30", path=data_path)
    updated = service.set_enabled(alarm.id, False, path=data_path)
    assert updated.enabled is False
    alarms = service.list_alarms(path=data_path)
    assert alarms[0].enabled is False


def test_set_enabled_missing_alarm_raises(data_path):
    with pytest.raises(LookupError):
        service.set_enabled(999, True, path=data_path)


def test_get_due_alarms_matches_enabled_and_time(data_path):
    due = service.add_alarm("07:30", label="due", path=data_path)
    service.add_alarm("08:00", label="not due", path=data_path)
    disabled = service.add_alarm("07:30", label="disabled", path=data_path)
    service.set_enabled(disabled.id, False, path=data_path)

    result = service.get_due_alarms("07:30", path=data_path)

    assert [a.id for a in result] == [due.id]

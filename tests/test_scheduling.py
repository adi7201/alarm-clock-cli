import pytest

from alarm_clock import scheduler, service


@pytest.fixture
def data_path(tmp_path):
    return tmp_path / "alarm.json"


def test_tick_fires_due_alarm_and_removes_it(data_path, capsys):
    due = service.add_alarm("07:30", label="Wake up", path=data_path)
    not_due = service.add_alarm("08:00", label="Later", path=data_path)

    fired = scheduler.tick("07:30", path=data_path)

    assert [a.id for a in fired] == [due.id]
    remaining_ids = [a.id for a in service.list_alarms(path=data_path)]
    assert remaining_ids == [not_due.id]
    assert "Wake up" in capsys.readouterr().out


def test_tick_skips_disabled_alarm(data_path):
    alarm = service.add_alarm("07:30", path=data_path)
    service.set_enabled(alarm.id, False, path=data_path)

    fired = scheduler.tick("07:30", path=data_path)

    assert fired == []
    remaining_ids = [a.id for a in service.list_alarms(path=data_path)]
    assert remaining_ids == [alarm.id]


def test_tick_no_match_does_nothing(data_path):
    service.add_alarm("07:30", path=data_path)

    fired = scheduler.tick("09:00", path=data_path)

    assert fired == []
    assert len(service.list_alarms(path=data_path)) == 1

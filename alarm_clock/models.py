import re
from dataclasses import asdict, dataclass

TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def validate_time(time_str: str) -> str:
    if not TIME_RE.match(time_str):
        raise ValueError(
            f"Invalid time '{time_str}': expected 24-hour HH:MM (e.g. 07:30, 23:59)"
        )
    return time_str


@dataclass
class Alarm:
    id: int
    time: str
    label: str = ""
    enabled: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Alarm":
        return Alarm(**d)

from datetime import time

from typing_extensions import TypedDict


class UserConfig(TypedDict):
    employee_id: int
    checkin_time: time
    checkout_time: time

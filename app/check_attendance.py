import random
from datetime import UTC, datetime, timedelta

import odoorpc  # type: ignore[import-untyped]

from user_config import UserConfig


def check_attendance(odoo: odoorpc.ODOO, user_config: UserConfig) -> None:
    domain = [
        ("employee_id", "=", user_config.get("employee_id")),
        ("check_out", "=", False),  # Find records where check_out is not set
    ]
    active_attendance = odoo.execute(
        "hr.attendance", "search_read", domain, ["id", "check_in"]
    )

    now = datetime.now(UTC)

    checkin_time = now.replace(
        hour=user_config["checkin_time"].hour,
        minute=user_config["checkin_time"].minute,
        second=0,
        microsecond=0,
    )
    checkout_time = now.replace(
        hour=user_config["checkout_time"].hour,
        minute=user_config["checkout_time"].minute,
        second=0,
        microsecond=0,
    )

    if checkin_time < now < checkout_time:
        # running checking process
        if not active_attendance:
            # Employee is not checked in, so check them in
            randomized_checkin = _randomize_date(datetime.now(UTC), range_minutes=30)
            check_in_time = randomized_checkin.strftime("%Y-%m-%d %H:%M:%S")
            attendance_values = {
                "employee_id": user_config.get("employee_id"),
                "check_in": check_in_time,
            }
            odoo.execute("hr.attendance", "create", attendance_values)
            print(f"Checked in successfully at {check_in_time}")
        else:
            # Employee already checked in manually, so do nothing
            print("Already checked in")
            return

    elif now > checkout_time:
        # running checkout process
        if not active_attendance:
            # Employee already checked out manually, so do nothing
            print("Already checked out")
            return

        else:
            # Employee is checked in, so check them out
            attendance_id = active_attendance[0]["id"]
            check_in_time = active_attendance[0]["check_in"]

            randomized_checkout = _randomize_date(datetime.now(UTC), range_minutes=30)
            check_out_time = randomized_checkout.strftime("%Y-%m-%d %H:%M:%S")

            odoo.execute(
                "hr.attendance", "write", [attendance_id], {"check_out": check_out_time}
            )
            print(
                f"Checked out successfully! (Check-in: {check_in_time}, Check-out: {check_out_time})"
            )

    return


def _randomize_date(date: datetime, range_minutes: int = 30) -> datetime:
    # Randomize the date by adding random minutes: between -30 and +0 (to avoid checking in the future) by default
    random_minutes = random.randint(-range_minutes, 0)  # noqa: S311

    # add also random seconds
    random_seconds = random.randint(-60, 0)  # noqa: S311
    return date + timedelta(minutes=random_minutes) + timedelta(seconds=random_seconds)

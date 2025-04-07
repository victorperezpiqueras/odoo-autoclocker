import os
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import odoorpc  # type: ignore[import-untyped]


def handler(event: dict[str, Any], context: dict[str, Any]) -> None:
    try:
        print("Procesing event:", event, context)
        # Retrieve Odoo credentials from environment variables
        odoo_url = os.environ.get("ODOO_URL")
        odoo_db = os.environ.get("ODOO_DB")
        odoo_port = int(os.environ.get("ODOO_PORT", 443))
        odoo_version = os.environ.get("ODOO_VERSION")
        odoo_username = os.environ.get("ODOO_USERNAME")
        odoo_password = os.environ.get("ODOO_PASSWORD")
        employee_id = int(cast(str, os.environ.get("ODOO_EMPLOYEE_ID")))

        # Connect to Odoo
        odoo = odoorpc.ODOO(
            odoo_url, port=odoo_port, version=odoo_version, protocol="jsonrpc+ssl"
        )
        odoo.login(odoo_db, odoo_username, odoo_password)

        today = datetime.now(UTC)
        start_date = today - timedelta(days=1)
        end_date = today + timedelta(days=1)

        # Check if today is a holiday
        holidays = get_calendar_holidays(odoo, start_date=start_date, end_date=end_date)
        if today.date() in [h.date() for h in holidays]:
            print("Today is a holiday. Skipping attendance check.")
            return None

        absences = get_all_absences(
            odoo, employee_id, start_date=start_date, end_date=end_date
        )
        for absence in absences:
            if absence[0].date() <= today.date() <= absence[1].date():
                print("Employee is on leave. Skipping attendance check.")
                return None

        check_attendance(odoo, employee_id)
    except Exception as e:
        print(f"Error checking attendance: {str(e)}")
        return None


def get_calendar_holidays(
    odoo: odoorpc.ODOO, start_date: datetime, end_date: datetime
) -> list[datetime]:
    try:
        start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")

        unusual_days: dict[str, bool] = odoo.execute_kw(
            "hr.leave",
            "get_unusual_days",
            [start_date, end_date],
        )

        return [datetime.fromisoformat(k) for k, v in unusual_days.items() if v is True]

    except Exception as e:
        print(f"Error retrieving unusual days: {str(e)}")
        return []


def get_all_absences(
    odoo: odoorpc.ODOO, employee_id: int, start_date: datetime, end_date: datetime
) -> list[tuple[datetime, datetime]]:
    try:
        start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")

        leave_domain = [
            ("employee_id", "=", employee_id),
            (
                "state",
                "=",
                "validate",
            ),  # doesnt properly filter out non-approved leaves
            ("date_to", ">=", start_date),
            ("date_from", "<=", end_date),
        ]
        leaves = odoo.execute(
            "hr.leave",
            "search_read",
            leave_domain,
            ["date_from", "date_to", "display_name"],
        )
        return [
            (
                datetime.fromisoformat(leave["date_from"]),
                datetime.fromisoformat(leave["date_to"]),
            )
            for leave in leaves
        ]

    except Exception as e:
        print(f"Error retrieving absences: {str(e)}")
        return []


def check_attendance(odoo: odoorpc.ODOO, employee_id: int) -> None:
    # Check if employee is already checked in
    domain = [
        ("employee_id", "=", employee_id),
        ("check_out", "=", False),  # Find records where check_out is not set
    ]
    active_attendance = odoo.execute(
        "hr.attendance", "search_read", domain, ["id", "check_in"]
    )

    if active_attendance:
        # Employee is checked in, so check them out
        attendance_id = active_attendance[0]["id"]
        check_in_time = active_attendance[0]["check_in"]
        check_out_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

        odoo.execute(
            "hr.attendance", "write", [attendance_id], {"check_out": check_out_time}
        )
        print(
            f"Checked out successfully! (Check-in: {check_in_time}, Check-out: {check_out_time})"
        )

    else:
        # Employee is not checked in, so check them in
        check_in_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        attendance_values = {"employee_id": employee_id, "check_in": check_in_time}
        odoo.execute("hr.attendance", "create", attendance_values)
        print(f"Checked in successfully at {check_in_time}")


# Example usage
if __name__ == "__main__":
    handler(event={}, context={})

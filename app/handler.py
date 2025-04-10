import os
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import odoorpc  # type: ignore[import-untyped]

from app.check_attendance import check_attendance
from app.get_all_absences import get_all_absences
from app.get_calendar_holidays import get_calendar_holidays
from app.user_config import UserConfig


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
        checkin_time_utc = datetime.strptime(
            os.environ.get("CHECKIN_TIME_UTC"), "%H:%M"
        ).time()
        checkout_time_utc = datetime.strptime(
            os.environ.get("CHECKOUT_TIME_UTC"), "%H:%M"
        ).time()

        user_config = UserConfig(
            employee_id=employee_id,
            checkin_time=checkin_time_utc,
            checkout_time=checkout_time_utc,
        )

        # Connect to Odoo
        odoo = odoorpc.ODOO(
            odoo_url, port=odoo_port, version=odoo_version, protocol="jsonrpc+ssl"
        )
        odoo.login(odoo_db, odoo_username, odoo_password)

        now = datetime.now(UTC)
        start_date = now - timedelta(days=1)
        end_date = now + timedelta(days=1)

        # Check if today is a holiday
        holidays = get_calendar_holidays(odoo, start_date=start_date, end_date=end_date)
        if now.date() in [h.date() for h in holidays]:
            print("Today is a holiday. Skipping attendance check.")
            return None

        absences = get_all_absences(
            odoo, user_config, start_date=start_date, end_date=end_date
        )
        for absence in absences:
            if absence[0].date() <= now.date() <= absence[1].date():
                print("Employee is on leave. Skipping attendance check.")
                return None

        check_attendance(odoo, user_config)
    except Exception as e:
        print(f"Error checking attendance: {str(e)}")
        return None


# Example usage
if __name__ == "__main__":
    handler(event={}, context={})

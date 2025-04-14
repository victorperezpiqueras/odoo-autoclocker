from datetime import datetime

import odoorpc  # type: ignore[import-untyped]


def get_calendar_holidays(
    odoo: odoorpc.ODOO, start_date: datetime, end_date: datetime
) -> list[datetime]:
    try:
        start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

        unusual_days: dict[str, bool] = odoo.execute_kw(
            "hr.leave",
            "get_unusual_days",
            [start_date_str, end_date_str],
        )

        return [datetime.fromisoformat(k) for k, v in unusual_days.items() if v is True]

    except Exception as e:
        print(f"Error retrieving unusual days: {str(e)}")
        return []

from datetime import datetime

import odoorpc  # type: ignore[import-untyped]

from user_config import UserConfig


def get_all_absences(
    odoo: odoorpc.ODOO,
    user_config: UserConfig,
    start_date: datetime,
    end_date: datetime,
) -> list[tuple[datetime, datetime]]:
    try:
        start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

        leave_domain = [
            ("employee_id", "=", user_config.get("employee_id")),
            (
                "state",
                "=",
                "validate",
            ),  # doesnt properly filter out non-approved leaves
            ("date_to", ">=", start_date_str),
            ("date_from", "<=", end_date_str),
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

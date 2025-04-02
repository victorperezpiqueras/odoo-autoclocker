import os
import odoorpc
from datetime import datetime


def check_attendance():
    """
    Check the current attendance status of the user and handle check-in/check-out accordingly.

    Returns:
        Dictionary with attendance details on success, None on failure.
    """
    try:
        # Retrieve Odoo credentials from environment variables
        odoo_url = os.environ.get("ODOO_URL")
        odoo_db = os.environ.get("ODOO_DB")
        odoo_port = int(os.environ.get("ODOO_PORT", 443))
        odoo_version = os.environ.get("ODOO_VERSION")
        odoo_username = os.environ.get("ODOO_USERNAME")
        odoo_password = os.environ.get("ODOO_PASSWORD")
        employee_id = int(os.environ.get("ODOO_EMPLOYEE_ID"))

        # Connect to Odoo
        odoo = odoorpc.ODOO(
            odoo_url, port=odoo_port, version=odoo_version, protocol="jsonrpc+ssl"
        )
        odoo.login(odoo_db, odoo_username, odoo_password)

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
            check_out_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            odoo.execute(
                "hr.attendance", "write", [attendance_id], {"check_out": check_out_time}
            )
            print(
                f"Checked out successfully! (Check-in: {check_in_time}, Check-out: {check_out_time})"
            )

            return {
                "attendance_id": attendance_id,
                "check_in": check_in_time,
                "check_out": check_out_time,
            }

        else:
            # Employee is not checked in, so check them in
            check_in_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            attendance_data = {"employee_id": employee_id, "check_in": check_in_time}
            attendance_id = odoo.execute("hr.attendance", "create", attendance_data)

            print(f"Checked in successfully at {check_in_time}")

            return {
                "attendance_id": attendance_id,
                "check_in": check_in_time,
                "check_out": None,
            }

    except Exception as e:
        print(f"Error checking attendance: {str(e)}")
        return None


# Example usage
if __name__ == "__main__":
    check_attendance()

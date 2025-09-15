import os
import sys
import json
import argparse
import gspread
from google.oauth2.service_account import Credentials


class GoogleSheetUpdater:
    def __init__(self, spreadsheet_id, sheet_name,
                 service_account_file=None, env_var="GOOGLE_SHEET_CREDENTIALS"):
        """
        :param spreadsheet_id: Google Sheet ID
        :param sheet_name: tên sheet/tab
        :param service_account_file: path file JSON (chỉ dùng cho dev)
        :param env_var: tên biến môi trường chứa key (prod)
        """
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name

        # Mode lấy từ biến môi trường (default: dev)
        mode = os.getenv("MODE", "dev").lower()

        if mode == "dev":
            if not service_account_file:
                raise ValueError("Dev mode yêu cầu service_account_file")
            creds = Credentials.from_service_account_file(
                service_account_file,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
        elif mode == "prod":
            creds_json = os.getenv(env_var)
            if not creds_json:
                raise ValueError(f"Prod mode yêu cầu biến môi trường {env_var}")
            creds_dict = json.loads(creds_json)

            # Fix lỗi \n trong private_key
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
        else:
            raise ValueError("MODE chỉ có thể là 'dev' hoặc 'prod'")

        # Khởi tạo client
        client = gspread.authorize(creds)
        self.sheet = client.open_by_key(self.spreadsheet_id).worksheet(self.sheet_name)

        # Map cột -> cell
        self.column_map = {
            "Centos": "A6", "Redhat": "B6", "Oracle Linux": "C6", "OS_Other": "D6",
            "Tomcat": "E6", "Weblogic": "F6", "Nginx": "G6", "Apache": "H6",
            "Jetty": "I6", "WebServer_Other": "J6", "Oracle": "K6", "Mysql": "L6",
            "MSSQL": "M6", "MongoDB": "N6", "Java": "O6", "Vsftp": "P6",
            "Memcache": "Q6", "Redis": "R6", "ESXi": "S6"
        }

    def update_column(self, column_name, value):
        """Update một cột theo tên"""
        if column_name not in self.column_map:
            raise ValueError(f"Column '{column_name}' không tồn tại trong map")
        cell = self.column_map[column_name]
        self.sheet.update(cell, [[value]])
        print(f"Updated {column_name} ({cell}) with value: {value}")

    def update_multi(self, data: dict):
        """Update nhiều cột"""
        for col, val in data.items():
            self.update_column(col, val)


# ===============================
# Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Google Sheet")
    parser.add_argument("--spreadsheet_id", required=True, help="Google Spreadsheet ID")
    parser.add_argument("--sheet_name", required=True, help="Tên sheet/tab")
    parser.add_argument("--service_account_file", help="Path JSON file (dev mode)")
    parser.add_argument("--data", help="Dữ liệu update, dạng JSON string (optional)")

    args = parser.parse_args()

    # Nếu không có --data thì đọc từ stdin (extra-vars @- của ansible)
    if args.data:
        try:
            update_data = json.loads(args.data)
        except json.JSONDecodeError as e:
            raise ValueError(f"--data không phải JSON hợp lệ: {e}")
    else:
        try:
            raw_input = sys.stdin.read().strip()
            update_data = json.loads(raw_input) if raw_input else {}
        except json.JSONDecodeError as e:
            raise ValueError(f"stdin không phải JSON hợp lệ: {e}")

    updater = GoogleSheetUpdater(
        spreadsheet_id=args.spreadsheet_id,
        sheet_name=args.sheet_name,
        service_account_file=args.service_account_file
    )

    updater.update_multi(update_data)

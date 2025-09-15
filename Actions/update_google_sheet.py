import os
import json
import gspread
from google.oauth2.service_account import Credentials


class GoogleSheetUpdater:
    def __init__(self, spreadsheet_id, sheet_name,
                 mode="dev", service_account_file=None, env_var="GOOGLE_SHEET_CREDENTIALS"):
        """
        :param spreadsheet_id: Google Sheet ID
        :param sheet_name: tên sheet/tab
        :param mode: "dev" hoặc "prod"
        :param service_account_file: path file JSON (chỉ dùng cho dev)
        :param env_var: tên biến môi trường chứa key (prod)
        """
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name

        # Khởi tạo credentials theo mode
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
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
        else:
            raise ValueError("Mode chỉ có thể là 'dev' hoặc 'prod'")

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
# Demo sử dụng
if __name__ == "__main__":
    SPREADSHEET_ID = "1f-fHFE18Ipmzl_zyMh5-Jf5Mxn3xsd1fvuIPHn-dj44"
    SHEET_NAME = "Sheet1"

    # Case DEV (local file)
    # updater = GoogleSheetUpdater(
    #     spreadsheet_id=SPREADSHEET_ID,
    #     sheet_name=SHEET_NAME,
    #     mode="dev",
    #     service_account_file="./Configs/service_account.json"
    # )

    # Case PROD (env var, inject qua Ansible Vault)
    updater = GoogleSheetUpdater(
        spreadsheet_id=SPREADSHEET_ID,
        sheet_name=SHEET_NAME,
        mode="prod",
        env_var="GOOGLE_SHEET_CREDENTIALS"
    )

    updater.update_multi({
        "Centos": "Host1",
        "Nginx": "Running fast"
    })
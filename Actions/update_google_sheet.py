import gspread
from google.oauth2.service_account import Credentials

class GoogleSheetUpdater:
    def __init__(self, service_account_file, spreadsheet_id, sheet_name):
        self.service_account_file = service_account_file
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name

        # Khởi tạo kết nối
        creds = Credentials.from_service_account_file(
            self.service_account_file,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
        self.sheet = client.open_by_key(self.spreadsheet_id).worksheet(self.sheet_name)

        # Map column name -> cell (hàng 6)
        self.column_map = {
            "Centos": "A6",
            "Redhat": "B6",
            "Oracle Linux": "C6",
            "OS_Other": "D6",
            "Tomcat": "E6",
            "Weblogic": "F6",
            "Nginx": "G6",
            "Apache": "H6",
            "Jetty": "I6",
            "WebServer_Other": "J6",
            "Oracle": "K6",
            "Mysql": "L6",
            "MSSQL": "M6",
            "MongoDB": "N6",
            "Java": "O6",
            "Vsftp": "P6",
            "Memcache": "Q6",
            "Redis": "R6",
            "ESXi": "S6"
        }

    def update_column(self, column_name, value):
        """Update một cột theo tên"""
        if column_name not in self.column_map:
            raise ValueError(f"Column '{column_name}' not found in template map")
        cell = self.column_map[column_name]
        self.sheet.update(cell, [[value]])
        print(f"✅ Updated {column_name} ({cell}) with value: {value}")

    def update_multi(self, data: dict):
        """Update nhiều cột cùng lúc (dùng dict {col_name: value})"""
        for col, val in data.items():
            self.update_column(col, val)


# ============================
# Demo sử dụng
if __name__ == "__main__":
    SERVICE_ACCOUNT_FILE = "./Configs/autosecops_google_sheet.json"
    SPREADSHEET_ID = "1f-fHFE18Ipmzl_zyMh5-Jf5Mxn3xsd1fvuIPHn-dj44"
    SHEET_NAME = "Sheet1"

    updater = GoogleSheetUpdater(SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, SHEET_NAME)

    # Update một cột
    updater.update_column("Centos", "Host1")

    # Update nhiều cột cùng lúc
    updater.update_multi({
        "Redhat": "Uptime: 3 days",
        "Oracle Linux": "Disk 70%",
        "Nginx": "Running"
    })

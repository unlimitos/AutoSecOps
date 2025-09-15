# AutoSecOps

curl -X POST -H "Content-Type: application/x-www-form-urlencoded" \
-d "client_id=44e4363b-99d6-4e2d-84fc-dfd9441a7127" \
-d "scope=https://graph.microsoft.com/.default" \
-d "client_secret=Y4bT8Q~r11XV0RpJwMlfbkGFAp9AfGCRP0kr0Ab9M" \
-d "grant_type=client_credentials" \
https://login.microsoftonline.com/89a7f078-234b-46ee-a96e-0b8e8b347cbe/oauth2/v2.0/token

SPREADSHEET_ID = "1f-fHFE18Ipmzl_zyMh5-Jf5Mxn3xsd1fvuIPHn-dj44"
SHEET_NAME = "Sheet1"

# Thiết lập môi trường chạy python3
# python3 -m venv .venv
.venv\Scripts\activate

# Lện mã hoá api key
 ansible-vault encrypt ./Configs/autosecops_google_sheet.yml
# Lệnh descript ngược từ file mã hoá ra json
ansible-vault decrypt ./Configs/autosecops_google_sheet.json  --output ./Configs/service_account.json

echo '{"update_data": {"Centos": "Host1", "Nginx": "Running fast"}}'  | ansible-playbook ./Playbooks/update_google_sheet.yml  --extra-vars "$(cat -)"  --extra-vars "mode=prod" -i localhost, --ask-vault-pass  -vvv
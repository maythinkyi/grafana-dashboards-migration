import requests
import time
import sys

SOURCE_URL = "http://localhost:3001"
SOURCE_TOKEN = "source_token"

TARGET_URL = "http://localhost:3002"
TARGET_TOKEN = "destination_token"

def retry_api(func):
    def wrapper(*args, **kwargs):
        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as error:
                if error.response.status_code in [401, 403]:
                    raise error
                if attempt == 2: raise error
                time.sleep((attempt + 1) * 2)
        return None
    return wrapper

class GrafanaClient:
    def __init__(self, url, token):
        self.url = url.strip("/")
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    @retry_api
    def get(self, endpoint):
        res = requests.get(f"{self.url}{endpoint}", headers=self.headers, timeout=30)
        res.raise_for_status()
        return res.json()

    @retry_api
    def post(self, endpoint, payload):
        res = requests.post(f"{self.url}{endpoint}", headers=self.headers, json=payload, timeout=30)
        res.raise_for_status()
        return res.json()

class MigrationService:
    def __init__(self):
        self.source = GrafanaClient(SOURCE_URL, SOURCE_TOKEN)
        self.target = GrafanaClient(TARGET_URL, TARGET_TOKEN)
        self.folder_map = {}
        self.success_count = 0
        self.errors = []

    def run(self):
        try:
            source_folders = self.source.get("/api/folders")
            target_folders = self.target.get("/api/folders")

            try:
                existing_target_folders = {
                    target_folder["title"]: target_folder["uid"] 
                    for target_folder in target_folders
                }
            except:
                existing_target_folders = {}

            for source_folder in source_folders:
                folder_title = source_folder["title"]
                source_folder_uid = source_folder["uid"]

                if folder_title in existing_target_folders:
                    self.folder_map[source_folder_uid] = existing_target_folders[folder_title]
                else:
                    try:
                        new_folder = self.target.post("/api/folders", {"title": folder_title, "uid": source_folder_uid})
                        self.folder_map[source_folder_uid] = new_folder["uid"]
                    except Exception as folder_error:
                        self.errors.append(f"Folder '{folder_title}' failed: {folder_error}")

            dashboards = self.source.get("/api/search?type=dash-db")
            
            for dashboard in dashboards:
                dashboard_title = dashboard["title"]
                dashboard_uid = dashboard["uid"]
                
                try:
                    dashboard_payload = self.source.get(f"/api/dashboards/uid/{dashboard_uid}")["dashboard"]
                    dashboard_payload.pop("id", None)
                    dashboard_payload.pop("version", None)
                    
                    payload = {"dashboard": dashboard_payload, "overwrite": True}
                    
                    # Check if the dashboard belongs to a folder we mapped
                    source_parent_folder_uid = dashboard.get("folderUid")
                    if source_parent_folder_uid in self.folder_map:
                        payload["folderUid"] = self.folder_map[source_parent_folder_uid]
                    
                    self.target.post("/api/dashboards/db", payload)
                    self.success_count += 1
                except Exception as dashboard_error:
                    self.errors.append(f"Dashboard '{dashboard_title}' failed: {dashboard_error}")

            if not self.errors:
                print(f"[SUCCESS] All {self.success_count} Dashboards migrated.")
            else:
                print(f"[FAIL] Migration incomplete. {self.success_count} success, {len(self.errors)} failed.")
                for err in self.errors:
                    print(f" -> {err}")

        except Exception as system_critical_error:
            print(f"[FAIL] Migration aborted: {system_critical_error}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "migrate":
        MigrationService().run()
    else:
        print("Usage: python3 script.py migrate")
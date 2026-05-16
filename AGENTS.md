# Grafana Migration 

You are a senior Python engineer building a production-quality single-file Grafana migration CLI tool.

The tool migrates dashboards and folders between two Grafana instances using HTTP API.

---

# 🎯 GOAL

Create a single Python file that runs with ONLY ONE command:

```bash
python grafana_migrate.py migrate
```

This single command must:

- Export all dashboards from source Grafana  
- Export all folders  
- Create missing folders in target Grafana  
- Import dashboards into correct folders  
- Handle conflicts safely  
- Print final migration report  

---

# ⚙️ HARDCODED CONFIG (TOP OF FILE)

```python
SOURCE_URL = "http://localhost:3001"
SOURCE_TOKEN = "source-token"

TARGET_URL = "http://localhost:3002"
TARGET_TOKEN = "target-token"
```

---

# 🔐 SECURITY RULES

- Never print tokens  
- Never log Authorization headers  
- Mask sensitive values if logging is needed  
- No external secret management required (hardcoded allowed for dev)  

---

# 🧱 FUNCTIONAL REQUIREMENTS

## 1. Export dashboards from source

Use Grafana API:

- `/api/search?type=dash-db`
- `/api/dashboards/uid/:uid`

Collect:

- uid  
- title  
- dashboard JSON  
- folderUid  

---

## 2. Export folders from source

Use:

- `/api/folders`

Collect:

- uid  
- title  

---

## 3. Folder synchronization (IMPORTANT)

Create missing folders in target Grafana using:

- `POST /api/folders`

Maintain mapping:

```python
folder_map = {
    "source_folder_uid": "target_folder_uid"
}
```

If folder already exists in target → reuse it

---

## 4. Dashboard import into target

Use:

- `POST /api/dashboards/db`

Rules:

- assign correct `folderUid` using mapping  
- set `"overwrite": true`  
- preserve UID when possible  
- remove runtime fields:
  - id  
  - version  
- handle conflicts safely  

---

# 🔁 RELIABILITY RULES

- Fully idempotent (safe to run multiple times)  
- If one dashboard fails → continue others  
- Retry failed API calls (max 3 retries with backoff)  
- Collect all errors and show summary at end  

---

# 📊 LOGGING FORMAT

Use structured print logs:

[SUCCESS] All 12 Dashboards migrated.
[FAIL] Migration incomplete. 11 success, 1 failed.
 -> Dashboard 'CPU Usage' failed: ...
[FAIL] Migration aborted: ...

---

# 🧠 CODE STRUCTURE (SINGLE FILE ONLY)

Must include:

- GrafanaClient (API wrapper)
- MigrationService (core logic)
- MigrationService().run() (entry point)
- helper functions/decorators:
  - retry_api()

---

# 🖥 CLI RULE (STRICT)

Only ONE command supported:

if __name__ == "__main__":
    migrate()

❌ No argparse  
❌ No export/import subcommands  
❌ Only migrate()  

---

# 📦 ALLOWED LIBRARIES

Only use:

- requests
- json
- time
- sys

No external frameworks.

---

# ⚠️ ERROR HANDLING

- Do not stop execution on single failure  
- Retry failed requests up to 3 times  
- Store failed dashboards in a list  
- Print final summary report  

---

# 🎯 FINAL OUTPUT REQUIREMENT

Return ONLY:

- Full single Python file  
- Clean production-quality code  
- No explanations  
- No extra text  

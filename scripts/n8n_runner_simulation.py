import os
import httpx
from datetime import datetime

os.makedirs('n8n_downloads', exist_ok=True)

base_url = "http://localhost:8000"

shifts = [
    {
        "name": "Shift 1: Day Bulletin (08:00 AM - 05:00 PM)",
        "cron": "0 17 * * * (5:00 PM)",
        "payload": {
            "title": "Shift 1 Day Bulletin (08:00 AM - 05:00 PM)",
            "report_type": "Shift 1: Day Bulletin (8:00 AM - 5:00 PM)"
        },
        "filename": "n8n_shift1_day_bulletin.pdf"
    },
    {
        "name": "Shift 2: Evening Bulletin (05:00 PM - 09:00 PM)",
        "cron": "0 21 * * * (9:00 PM)",
        "payload": {
            "title": "Shift 2 Evening Bulletin (05:00 PM - 09:00 PM)",
            "report_type": "Shift 2: Evening Bulletin (5:00 PM - 9:00 PM)"
        },
        "filename": "n8n_shift2_evening_bulletin.pdf"
    },
    {
        "name": "Shift 3: Night & Early Morning Bulletin (09:00 PM - 08:00 AM)",
        "cron": "0 8 * * * (8:00 AM)",
        "payload": {
            "title": "Shift 3 Night Bulletin (09:00 PM - 08:00 AM)",
            "report_type": "Shift 3: Night & Early Morning Bulletin (9:00 PM - 8:00 AM)"
        },
        "filename": "n8n_shift3_night_bulletin.pdf"
    }
]

print("=== Starting n8n Self-Hosted Automation Execution ===")

for shift in shifts:
    print(f"\n[n8n Trigger] Executing Cron: {shift['cron']} for '{shift['name']}'...")
    # Step 1: HTTP Request Node (POST /api/pdf/generate)
    res_gen = httpx.post(f"{base_url}/api/pdf/generate", json=shift['payload']).json()
    report_id = res_gen['id']
    download_url = res_gen['download_url']
    article_count = res_gen['article_count']
    print(f" -> HTTP POST /api/pdf/generate Success! Report ID: {report_id}, Articles: {article_count}")

    # Step 2: HTTP Request Node (GET download binary)
    res_bin = httpx.get(f"{base_url}{download_url}")
    print(f" -> HTTP GET {download_url} Binary Download Status: {res_bin.status_code}")

    # Step 3: Write Binary File Node
    target_path = os.path.join('n8n_downloads', shift['filename'])
    with open(target_path, 'wb') as f:
        f.write(res_bin.content)
    print(f" -> Write Binary File Node: Saved {len(res_bin.content)} bytes to '{target_path}'")

print("\n=== n8n Automation Execution Completed Successfully! All 3 Shift PDFs Saved. ===")

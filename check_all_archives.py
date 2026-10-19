
import pandas as pd
import requests
from pathlib import Path
from urllib.parse import urldefrag
import time

# Find our project folder and spreadsheet.
folder = Path(__file__).parent
df = pd.read_excel(folder / "incubators.xlsx", sheet_name=0)

# Internet Archive's search service.
api_url = "https://web.archive.org/cdx/search/cdx"

# Create all 57 months from January 2022 to September 2026.
months = pd.date_range(
    start="2022-01-01",
    end="2026-09-01",
    freq="MS"
).strftime("%Y-%m").tolist()

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

results = []

for index, row in df.iterrows():
    name = str(row["Name"]).strip()

    pages = [
        ("homepage", row["Official_Website"]),
        ("about", row["About_URL"])
    ]

    for page_type, url in pages:

        if pd.isna(url) or not str(url).strip():
            print("Missing URL:", name, page_type)

            for month in months:
                results.append({
                    "Incubator": name,
                    "Page_Type": page_type,
                    "Month": month,
                    "Capture_Timestamp": "",
                    "Archived_URL": "",
                    "Status": "Missing URL"
                })
            continue

        # Remove fragments such as # from the URL.
        url = urldefrag(str(url).strip()).url

        params = {
            "url": url,
            "matchType": "exact",
            "output": "json",
            "filter": "statuscode:200",
            "from": "202201",
            "to": "202609",
            "fl": "timestamp,original,statuscode",
            "collapse": "timestamp:6"
        }

        print("\nChecking:", name, "|", page_type)

        captures_by_month = {}

        try:
            response = session.get(
                api_url,
                params=params,
                timeout=60
            )
            response.raise_for_status()
            captures = response.json()

            for capture in captures[1:]:
                timestamp, original_url, status = capture
                month = timestamp[:4] + "-" + timestamp[4:6]

                if month not in captures_by_month:
                    captures_by_month[month] = capture

            print("Months with captures:", len(captures_by_month))

            for month in months:
                capture = captures_by_month.get(month)

                if capture:
                    timestamp, original_url, status = capture

                    results.append({
                        "Incubator": name,
                        "Page_Type": page_type,
                        "Month": month,
                        "Capture_Timestamp": timestamp,
                        "Archived_URL": original_url,
                        "Status": "Capture found"
                    })
                else:
                    results.append({
                        "Incubator": name,
                        "Page_Type": page_type,
                        "Month": month,
                        "Capture_Timestamp": "",
                        "Archived_URL": "",
                        "Status": "No capture found"
                    })

        except (requests.RequestException, ValueError) as error:
            print("Archive lookup failed:", error)

            for month in months:
                results.append({
                    "Incubator": name,
                    "Page_Type": page_type,
                    "Month": month,
                    "Capture_Timestamp": "",
                    "Archived_URL": "",
                    "Status": "Lookup error"
                })

        # Pause between requests.
        time.sleep(1)

# Save the archive availability report.
report = pd.DataFrame(results)
report_file = folder / "archive_capture_index.csv"
report.to_csv(report_file, index=False)

print("\nArchive lookup finished.")
print("Total rows in report:", len(report))
print("\nResults:")
print(report["Status"].value_counts().to_string())
print("\nSaved report:", report_file)

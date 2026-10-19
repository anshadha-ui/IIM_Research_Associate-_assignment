
import requests
from pathlib import Path
import time

website_url = "https://bhau.org/"
api_url = "https://web.archive.org/cdx/search/cdx"

# Save files inside a new folder
project_folder = Path(__file__).parent
output_folder = project_folder / "bhau_monthly_archives"
output_folder.mkdir(exist_ok=True)

params = {
    "url": website_url,
    "output": "json",
    "filter": "statuscode:200",
    "from": "202201",
    "to": "202609",
    "fl": "timestamp,original,statuscode",
    "collapse": "timestamp:6"
}

print("Finding archived homepage captures...")

response = requests.get(api_url, params=params, timeout=60)
response.raise_for_status()
captures = response.json()

earliest_by_month = {}

for capture in captures[1:]:
    timestamp, original_url, status = capture
    month = timestamp[:4] + "-" + timestamp[4:6]

    if month not in earliest_by_month:
        earliest_by_month[month] = capture

print("Months found:", len(earliest_by_month))
print("Starting downloads...\n")

for month in sorted(earliest_by_month):
    timestamp, original_url, status = earliest_by_month[month]

    filename = f"homepage_{month}_{timestamp}.html"
    output_file = output_folder / filename

    # Skip files already downloaded successfully
    if output_file.exists() and output_file.stat().st_size > 0:
        print("Already downloaded:", filename)
        continue

    archive_url = (
        f"https://web.archive.org/web/{timestamp}id_/{original_url}"
    )

    try:
        page_response = requests.get(archive_url, timeout=60)
        page_response.raise_for_status()

        content = page_response.content

        if not content.strip():
            print("Empty response:", month)
            continue

        output_file.write_bytes(content)

        print(
            "Downloaded:", month,
            "| Size:", len(content), "bytes",
            "| File:", filename
        )

    except requests.RequestException as error:
        print("Download failed:", month, "| Error:", error)

    time.sleep(1)

print("\nFinished. Check the bhau_monthly_archives folder.")

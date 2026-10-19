

import requests
from pathlib import Path
import time

website_url = "https://bhau.org/"
api_url = "https://web.archive.org/cdx/search/cdx"

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

print("Finding archived captures...")

response = requests.get(api_url, params=params, timeout=60)
response.raise_for_status()
captures = response.json()

earliest_by_month = {}

for capture in captures[1:]:
    timestamp, original_url, status = capture
    month = timestamp[:6]

    if month not in earliest_by_month:
        earliest_by_month[month] = capture

print("Months found:", len(earliest_by_month))

success_count = 0
failed_months = []

for month in sorted(earliest_by_month):
    timestamp, original_url, status = earliest_by_month[month]

    readable_month = timestamp[:4] + "-" + timestamp[4:6]
    filename = f"homepage_{readable_month}_{timestamp}.html"
    output_file = output_folder / filename

    # Keep existing files so successful downloads are not repeated.
    if output_file.exists() and output_file.stat().st_size > 0:
        print("Already saved:", readable_month)
        success_count += 1
        continue

    archive_url = (
        f"https://web.archive.org/web/{timestamp}id_/{original_url}"
    )

    downloaded = False

    for attempt in range(1, 4):
        try:
            print(
                f"Downloading {readable_month} "
                f"(attempt {attempt}/3)..."
            )

            page_response = requests.get(
                archive_url,
                timeout=60,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            page_response.raise_for_status()

            content = page_response.content
            text_start = content[:5000].lower()

            if not content.strip():
                raise ValueError("The response is empty.")

            if (
                b"service unavailable" in text_start
                or b"too many requests" in text_start
            ):
                raise ValueError("The archive returned an error page.")

            if b"<html" not in text_start and b"<!doctype html" not in text_start:
                raise ValueError("HTML markup was not detected.")

            output_file.write_bytes(content)

            print(
                f"Saved {readable_month}: "
                f"{len(content):,} bytes"
            )

            downloaded = True
            success_count += 1
            break

        except (requests.RequestException, ValueError) as error:
            print("Attempt failed:", error)

            if attempt < 3:
                time.sleep(5 * attempt)

    if not downloaded:
        failed_months.append(readable_month)
        print("Could not download:", readable_month)

    time.sleep(3)

print("\n----- SUMMARY -----")
print("Successful or already saved:", success_count)
print("Failed months:", len(failed_months))
print("Failed month list:", failed_months)
print("Folder:", output_folder)

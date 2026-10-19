
import pandas as pd
import requests
import time
from pathlib import Path

# 1. Find the project folder and read the capture index.
folder = Path(__file__).parent

report = pd.read_csv(
    folder / "archive_capture_index.csv",
    dtype={"Capture_Timestamp": str}
)

# 2. Keep only rows where the Internet Archive has a capture.
available = report[report["Status"] == "Capture found"].copy()

print("Total captures to process:", len(available))

# 3. Prepare a file for recording download results.
log_file = folder / "archive_download_log.csv"

if log_file.exists():
    log = pd.read_csv(log_file)
else:
    log = pd.DataFrame(columns=[
        "Incubator", "Page_Type", "Month", "Capture_Timestamp",
        "Download_Status", "File_Path", "Bytes", "Error"
    ])

# 4. Create a web session for making requests.
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

# 5. Process each available capture.
for number, (_, row) in enumerate(available.iterrows(), start=1):

    incubator = str(row["Incubator"])
    page_type = str(row["Page_Type"])
    month = str(row["Month"])
    timestamp = str(row["Capture_Timestamp"]).replace(".0", "")
    original_url = str(row["Archived_URL"])

    # Build the output folder.
    safe_name = "".join(
        char if char.isalnum() or char in "-_ " else "_"
        for char in incubator
    ).strip().replace(" ", "_")

    output_folder = (
        folder / "archived_pages" / safe_name / page_type
    )
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = output_folder / f"{month}_{timestamp}.html"

    # Skip a file only if it exists and contains HTML markup.
    if output_file.exists():
        existing_content = output_file.read_bytes()[:10000].lower()

        if (
            b"<html" in existing_content
            or b"<!doctype html" in existing_content
        ):
            print(f"[{number}/{len(available)}] Already downloaded: {incubator} | {month}")
            continue

    # Construct the archived webpage URL.
    archive_url = (
        f"https://web.archive.org/web/{timestamp}id_/{original_url}"
    )

    success = False
    error_message = ""
    content_size = 0

    # Try up to three times if the request fails.
    for attempt in range(1, 4):
        try:
            response = session.get(archive_url, timeout=60)
            response.raise_for_status()

            content = response.content
            beginning = content[:10000].lower()

            if (
                b"<html" not in beginning
                and b"<!doctype html" not in beginning
            ):
                raise ValueError("HTML markup was not detected.")

            output_file.write_bytes(content)
            content_size = len(content)
            success = True
            break

        except Exception as error:
            error_message = str(error)
            print(
                f"  Attempt {attempt}/3 failed: {error_message}"
            )

            if attempt < 3:
                time.sleep(5 * attempt)

    # Record the result immediately, so progress is not lost.
    result = {
        "Incubator": incubator,
        "Page_Type": page_type,
        "Month": month,
        "Capture_Timestamp": timestamp,
        "Download_Status": "Success" if success else "Failed",
        "File_Path": str(output_file) if success else "",
        "Bytes": content_size,
        "Error": error_message if not success else ""
    }

    log = pd.concat(
        [log, pd.DataFrame([result])],
        ignore_index=True
    )
    log.to_csv(log_file, index=False)

    if success:
        print(
            f"[{number}/{len(available)}] SUCCESS: "
            f"{incubator} | {page_type} | {month} | "
            f"{content_size:,} bytes"
        )
    else:
        print(
            f"[{number}/{len(available)}] FAILED: "
            f"{incubator} | {page_type} | {month}"
        )

    # Pause between requests.
    time.sleep(2)

print("\nDownload process finished.")
print("Progress log:", log_file)
print("Archived files folder:", folder / "archived_pages")

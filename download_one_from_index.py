
import pandas as pd
import requests
from pathlib import Path

# Find the project folder.
folder = Path(__file__).parent

# Read our archive availability report.
report = pd.read_csv(
    folder / "archive_capture_index.csv",
    dtype={"Capture_Timestamp": str}
)

# Keep only rows where a capture was found.
available = report[report["Status"] == "Capture found"]

print("Available captures:", len(available))

# Select the first available capture.
row = available.iloc[0]

print("\nSelected incubator:", row["Incubator"])
print("Page type:", row["Page_Type"])
print("Month:", row["Month"])
print("Timestamp:", row["Capture_Timestamp"])
print("Original URL:", row["Archived_URL"])

# Build the Internet Archive download URL.
timestamp = str(row["Capture_Timestamp"]).replace(".0", "")
original_url = row["Archived_URL"]

archive_url = (
    f"https://web.archive.org/web/{timestamp}id_/{original_url}"
)

print("\nDownloading archived HTML...")

response = requests.get(
    archive_url,
    timeout=60,
    headers={"User-Agent": "Mozilla/5.0"}
)
response.raise_for_status()

content = response.content

# Check for basic HTML markup.
beginning = content[:10000].lower()

if (
    b"<html" not in beginning
    and b"<!doctype html" not in beginning
):
    raise ValueError("HTML markup was not detected.")

# Create a folder for this incubator and page type.
incubator_name = str(row["Incubator"])
safe_name = "".join(
    char if char.isalnum() or char in "-_ " else "_"
    for char in incubator_name
).strip().replace(" ", "_")

page_type = str(row["Page_Type"])
month = str(row["Month"])

output_folder = folder / "archived_pages" / safe_name / page_type
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / f"{month}_{timestamp}.html"
output_file.write_bytes(content)

print("\nDownload successful!")
print("File size:", len(content), "bytes")
print("Saved to:", output_file)

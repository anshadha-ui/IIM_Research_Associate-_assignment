
import requests
from pathlib import Path

# The archived webpage we found in our previous test
timestamp = "20220127061906"
website_url = "https://bhau.org/"

# Build the Wayback Machine replay URL
archive_url = (
    f"https://web.archive.org/web/{timestamp}id_/{website_url}"
)

# Create a folder for downloaded HTML files
output_folder = Path(__file__).parent / "test_downloads"
output_folder.mkdir(exist_ok=True)

# Choose the filename
output_file = output_folder / "bhau_homepage_2022-01.html"

print("Downloading archived webpage...")

try:
    response = requests.get(archive_url, timeout=60)
    response.raise_for_status()

    # Save the webpage's HTML content
    output_file.write_bytes(response.content)

    print("Download successful!")
    print("Saved file:", output_file)
    print("File size:", output_file.stat().st_size, "bytes")

except requests.RequestException as error:
    print("Download failed:", error)

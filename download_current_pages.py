
import pandas as pd
import requests
from pathlib import Path
import re
import time

# Find our project folder.
folder = Path(__file__).parent

# Read the Excel spreadsheet.
df = pd.read_excel(folder / "incubators.xlsx", sheet_name=0)

# Create a folder to store downloaded pages.
output_folder = folder / "current_pages"
output_folder.mkdir(exist_ok=True)

# Prepare a web session.
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

# Clean names so they can be used in filenames.
def clean_name(name):
    name = re.sub(r'[<>:"/\\|?*]', "", str(name))
    name = re.sub(r"\s+", "_", name.strip())
    return name[:80]

# Keep a record of our results.
results = []

# Visit every incubator.
for index, row in df.iterrows():
    name = str(row["Name"]).strip()
    folder_name = clean_name(name)

    # Create one folder for this incubator.
    incubator_folder = output_folder / folder_name
    incubator_folder.mkdir(exist_ok=True)

    # Check homepage and About page.
    pages = [
        ("homepage", row["Official_Website"]),
        ("about", row["About_URL"])
    ]

    for page_type, url in pages:

        # Skip a missing URL.
        if pd.isna(url) or not str(url).strip():
            print("SKIPPED:", name, "|", page_type, "| URL missing")
            results.append({
                "Incubator": name,
                "Page": page_type,
                "URL": "",
                "Status": "Missing URL"
            })
            continue

        url = str(url).strip()
        output_file = incubator_folder / f"{page_type}_current.html"

        try:
            print("Downloading:", name, "|", page_type)

            response = session.get(url, timeout=30)
            response.raise_for_status()

            # Save the downloaded page.
            output_file.write_bytes(response.content)

            print("SAVED:", output_file.name)

            results.append({
                "Incubator": name,
                "Page": page_type,
                "URL": url,
                "Status": f"HTTP {response.status_code}"
            })

        except requests.RequestException as error:
            print("FAILED:", name, "|", page_type, "|", error)

            results.append({
                "Incubator": name,
                "Page": page_type,
                "URL": url,
                "Status": f"Error: {error}"
            })

        # Pause briefly between requests.
        time.sleep(1)

# Save the results as a CSV file.
results_df = pd.DataFrame(results)
results_df.to_csv(folder / "current_pages_log.csv", index=False)

print("\nFinished downloading current pages.")
print("Results log: current_pages_log.csv")
print("Saved pages folder: current_pages")

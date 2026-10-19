

import pandas as pd
from pathlib import Path

# Locate the Excel file
folder = Path(__file__).parent
excel_file = folder / "incubators.xlsx"

# Read the first sheet
df = pd.read_excel(excel_file, sheet_name=0)

# Display the website columns
print("Available columns:")
print(df.columns.tolist())

print("\nIncubator names and website URLs:")

for index, row in df.iterrows():
    print("\nIncubator:", row.get("Name", "Name column not found"))
    print("Homepage:", row.get("Official_Website", "Column not found"))
    print("About page:", row.get("About_URL", "Column not found"))

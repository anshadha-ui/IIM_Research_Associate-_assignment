
import pandas as pd
from pathlib import Path

# Find the folder where this Python file is saved.
folder = Path(__file__).parent

# Find the Excel spreadsheet.
excel_file = folder / "incubators.xlsx"

# Read the first sheet of the spreadsheet.
df = pd.read_excel(excel_file, sheet_name=0)

# Show the number of rows.
print("Total rows:", len(df))

# Count rows that have an incubator name.
print("Rows with names:", df["Name"].notna().sum())

# Show each incubator and its website links.
for index, row in df.iterrows():
    print("\nIncubator number:", index + 1)
    print("Name:", row["Name"])
    print("Homepage:", row["Official_Website"])
    print("About page:", row["About_URL"])

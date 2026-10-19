
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).parent
excel_file = project_folder / "incubators.xlsx"

df = pd.read_excel(excel_file, sheet_name=0)

print("Total rows in spreadsheet:", len(df))
print("\nAvailable columns:")
print(df.columns.tolist())

print("\nFirst five incubators and their URLs:\n")

for index, row in df.head(5).iterrows():
    print("Incubator:", row.get("Name"))
    print("Homepage:", row.get("Official_Website"))
    print("About page:", row.get("About_URL"))
    print("-" * 50)


import pandas as pd
from pathlib import Path

folder = Path(__file__).parent
log_file = folder / "current_pages_log.csv"

# Read the download report.
df = pd.read_csv(log_file)

print("Total page attempts:", len(df))

print("\nResults by status:")
print(df["Status"].value_counts().to_string())

print("\nPages that were not downloaded successfully:")

# Show errors and missing URLs.
problems = df[
    df["Status"].str.startswith("Error")
    | (df["Status"] == "Missing URL")
]

if problems.empty:
    print("No problems found.")
else:
    print(problems[["Incubator", "Page", "URL", "Status"]].to_string(index=False))

print("\nSummary complete.")


from pathlib import Path

# 1. Locate the project folder.
folder = Path(__file__).parent
archive_folder = folder / "archived_pages"

# 2. Find every HTML file in the archive folders.
html_files = list(archive_folder.rglob("*.html"))

# 3. Prepare counters and a list for problems.
valid = 0
invalid = []

print("Starting HTML file verification...")
print("Please wait; checking", len(html_files), "files.\n")

# 4. Check each file.
for file in html_files:
    try:
        # Read the file's contents.
        content = file.read_bytes()

        # Inspect the first 10,000 bytes for HTML markup.
        beginning = content[:10000].lower()

        # Check that the file is large enough and contains HTML.
        if (
            len(content) > 1000
            and (
                b"<html" in beginning
                or b"<!doctype html" in beginning
            )
        ):
            valid += 1
        else:
            invalid.append(
                f"{file.name} | File is too small or HTML markup is missing"
            )

    except OSError as error:
        # Record file-access errors without stopping the script.
        invalid.append(f"{file.name} | Error: {error}")

# 5. Display the verification results.
print("\nVERIFICATION RESULTS")
print("--------------------")
print("Total HTML files found:", len(html_files))
print("Files passing basic HTML check:", valid)
print("Files failing check:", len(invalid))

# 6. Show files that need further inspection.
if invalid:
    print("\nFirst 20 files needing inspection:")
    for problem in invalid[:20]:
        print(problem)
else:
    print("\nAll files passed the basic HTML check.")

# 7. Save the list of files needing inspection.
report_file = folder / "archive_verification_issues.txt"

with open(report_file, "w", encoding="utf-8") as report:
    if invalid:
        report.write("\n".join(invalid))
    else:
        report.write("No files failed the basic HTML check.")

print("\nIssue report saved to:", report_file)

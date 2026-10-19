
from pathlib import Path

folder = Path(__file__).parent / "bhau_monthly_archives"
files = sorted(folder.glob("*.html"))

print("Total HTML files:", len(files))

valid_count = 0
invalid_files = []

for file in files:
    content = file.read_bytes()
    beginning = content[:10000].lower()

    looks_like_html = (
        b"<html" in beginning
        or b"<!doctype html" in beginning
    )

    if looks_like_html and len(content) > 1000:
        valid_count += 1
    else:
        invalid_files.append(file.name)

print("Files passing basic HTML checks:", valid_count)
print("Files needing inspection:", len(invalid_files))

for name in invalid_files:
    print("Check:", name)
print("Files passing basic HTML checks:", valid_count)
print("Files needing inspection:", len(invalid_files))

for name in invalid_files:
    print("Check:", name)
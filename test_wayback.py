
import requests

api_url = "https://web.archive.org/cdx/search/cdx"

# We will test with one website
website_url = "https://bhau.org/"

params = {
    "url": website_url,
    "output": "json",
    "filter": "statuscode:200",
    "from": "2022",
    "to": "2026",
    "fl": "timestamp,original,statuscode",
    "collapse": "timestamp:6"
}

print("Connecting to the Wayback Machine...")

try:
    response = requests.get(api_url, params=params, timeout=30)
    response.raise_for_status()

    captures = response.json()

    if len(captures) > 1:
        print("\nSuccess! Archived captures were found.")
        print("First few results:")

        for capture in captures[1:6]:
            print(capture)

    else:
        print("\nNo matching captures were returned for this test.")

except requests.RequestException as error:
    print("A website connection error occurred:", error)

except ValueError:
    print("The response was not valid JSON.")
    print(response.text[:500])

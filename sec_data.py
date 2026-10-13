
import requests

print("Connecting to SEC EDGAR...")

# NVIDIA's SEC company identifier
cik = "0001045810"

# SEC Company Facts API
url = (
    "https://data.sec.gov/api/xbrl/companyfacts/"
    f"CIK{cik}.json"
)

# Replace with your own contact information
headers = {
    "User-Agent": "EquityResearchStudent qilanli0908@gmail.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov"
}

try:
    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    print("\nConnection successful!")
    print("Company:", data.get("entityName"))
    print("CIK:", data.get("cik"))

    # Inspect available financial categories
    print("\nAvailable financial categories:")

    for category in data.get("facts", {}):
        print("-", category)

except requests.exceptions.RequestException as error:
    print("\nConnection failed:")
    print(error)

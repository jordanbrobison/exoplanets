import requests

API_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

def test_connection():
    params = {
        'query': 'select top 10 pl_name, hostname, disc_year from pscomppars',
        'format': 'json'
    }

    response = requests.get(API_URL, params=params)
    response.raise_for_status()

    data = response.json()
    for planet in data:
        print(f"{planet['pl_name']} {planet['hostname']}")

if __name__ == "__main__":
    test_connection()

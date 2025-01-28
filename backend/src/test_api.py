import json
import os

import requests

# Load test data from test_data.json
test_data_file = os.path.join(os.path.dirname(__file__), "test_data.json")

with open(test_data_file, "r") as file:
    payload = json.load(file)

# Endpoint URL
url = "http://127.0.0.1:4000/generate-metric-table"
# Send POST request
response = requests.get(url, json=payload, timeout=120)

# Print response
print("Status Code:", response.status_code)
print("Response JSON:", response.json())

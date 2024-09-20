import requests

# Define the URL
url = "http://10.91.55.46:8001/test"

# Define the JSON payload to send with the request
payload = {
    "key1": "value1",
    "key2": "value2"
}
print('lllll')

# Send the POST request with JSON data
response = requests.post(url, json=payload)

# Check the response status code and print the JSON response
if response.status_code == 200:
    print("Success!")
    try:
        response_json = response.json()  # Parse the JSON response
        print("Response JSON:", response_json)
    except ValueError:
        print("Failed to parse JSON response.")
else:
    print(f"Failed to get response. Status code: {response.status_code}")

import requests

url = "http://127.0.0.1:8000"
data = {"text": "My note"}
response = requests.post(url, data)

print(response.status_code)
print(response.json())

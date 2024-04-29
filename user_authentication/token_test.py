import requests

# Replace these with your actual username and password
username = 'lona'
password = 'lona1234'

data = {'username': username, 'password': password}

response = requests.post("http://127.0.0.1:8000/login/", data=data)

if response.status_code == 200:
    token = response.json().get('token', '')
    user_id = response.json().get('user_id', '')  # get the user's ID from the response

    print(f"Stored token in session: {token}")  # print the token
    print(f"Stored user ID in session: {user_id}")  # print the user ID
else:
    print('Invalid username or password')
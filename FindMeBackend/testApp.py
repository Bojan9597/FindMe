# test_api.py
import requests
import json

BASE_URL = 'http://127.0.0.1:5000'  # Update this if your Flask app is running on a different host or port

def create_user(username, email, password):
    url = f"{BASE_URL}/user"
    payload = {
        "username": username,
        "email": email,
        "password": password
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raises HTTPError for bad HTTP status codes
        response_json = response.json()
        print(f"Create User Response [{username}]:", response_json)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred during user creation [{username}]: {http_err}")
        print(f"Response content: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"Error occurred during user creation [{username}]: {err}")
    except json.JSONDecodeError:
        print(f"Non-JSON response received during user creation [{username}]:")
        print(response.text)
    return response

def login_user(username, password):
    url = f"{BASE_URL}/login"
    payload = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        response_json = response.json()
        print(f"Login User Response [{username}]:", response_json)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred during login [{username}]: {http_err}")
        print(f"Response content: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"Error occurred during login [{username}]: {err}")
    except json.JSONDecodeError:
        print(f"Non-JSON response received during login [{username}]:")
        print(response.text)
    return response

def main():
    print("---- Starting API Tests ----")

    # Test Case 1: Create User
    print("\n---- Test Case 1: Create User ----")
    response1 = create_user("john_doe", "john@example.com", "password1")
    user_id_1 = response1.json().get('user_id') if response1 and response1.status_code == 201 else None

    # Test Case 2: Attempt to Create Duplicate User
    print("\n---- Test Case 2: Attempt to Create Duplicate User ----")
    create_user("john_doe", "john@example.com", "password1")

    # Test Case 3: Login with Correct Credentials
    print("\n---- Test Case 3: Login with Correct Credentials ----")
    login_user("john_doe", "password1")

    # Test Case 4: Login with Incorrect Password
    print("\n---- Test Case 4: Login with Incorrect Password ----")
    login_user("john_doe", "wrong_password")

    # Test Case 5: Login with Non-existent User
    print("\n---- Test Case 5: Login with Non-existent User ----")
    login_user("non_existent_user", "password")

    # Test Case 6: Missing Required Fields in Login
    print("\n---- Test Case 6: Missing Required Fields in Login ----")
    login_user("", "")

    print("\n---- API Tests Completed ----")

if __name__ == "__main__":
    main()


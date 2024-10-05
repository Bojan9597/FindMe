# test_api.py
import requests
import json

BASE_URL = 'https://location.sharing.indigoingenium.ba'  # Update with your actual base URL if different

def create_user(username, email, password):
    url = f"{BASE_URL}/user"
    payload = {
        "username": username,
        "email": email,
        "password": password
    }
    response = requests.post(url, json=payload)
    print(f"Create User Response [{username}]:", response.json())
    return response

def update_user(user_id, username, email, password):
    url = f"{BASE_URL}/user/{user_id}"
    payload = {
        "username": username,
        "email": email,
        "password": password
    }
    response = requests.put(url, json=payload)
    print(f"Update User Response [{user_id}]:", response.json())
    return response

def add_or_update_location(user_id, latitude, longitude):
    url = f"{BASE_URL}/location"
    payload = {
        "user_id": user_id,
        "latitude": latitude,
        "longitude": longitude
    }
    response = requests.post(url, json=payload)
    print(f"Add/Update Location Response [{user_id}]:", response.json())
    return response

def get_location(user_id):
    url = f"{BASE_URL}/location/{user_id}"
    response = requests.get(url)
    print(f"Get Location Response [{user_id}]:", response.json())
    return response

def update_location_share(follower_id, following_id, is_approved=None):
    url = f"{BASE_URL}/location_share"
    payload = {
        "follower_id": follower_id,
        "following_id": following_id,
        "is_approved": is_approved
    }
    response = requests.post(url, json=payload)
    print(f"Update Location Share Response [{follower_id}->{following_id}]:", response.json())
    return response

def get_users():
    url = f"{BASE_URL}/users"
    response = requests.get(url)
    print("Get Users Response:", response.json())
    return response

def get_location_shares():
    url = f"{BASE_URL}/location_shares"
    response = requests.get(url)
    print("Get Location Shares Response:", response.json())
    return response

def main():
    print("---- Starting API Tests ----")

    # Test Case 1: Create Users
    print("\n---- Test Case 1: Create Users ----")
    response1 = create_user("john_doe", "john@example.com", "password1")
    user_id_1 = response1.json().get('user_id') if response1.status_code == 201 else None

    response2 = create_user("alice_smith", "alice@example.com", "password2")
    user_id_2 = response2.json().get('user_id') if response2.status_code == 201 else None

    # Test Case 2: Attempt to Create Duplicate User
    print("\n---- Test Case 2: Attempt to Create Duplicate User ----")
    create_user("john_doe", "john@example.com", "password1")

    # Test Case 3: Update User
    print("\n---- Test Case 3: Update User ----")
    if user_id_1:
        update_user(user_id_1, "john_doe_updated", "john_new@example.com", "new_password1")

    # Test Case 4: Attempt to Update Non-existent User
    print("\n---- Test Case 4: Attempt to Update Non-existent User ----")
    update_user(9999, "ghost_user", "ghost@example.com", "password")

    # Test Case 5: Add or Update Location
    print("\n---- Test Case 5: Add or Update Location ----")
    if user_id_1:
        add_or_update_location(user_id_1, 40.7128, -74.0060)  # New York City coordinates

    # Test Case 6: Get User Location
    print("\n---- Test Case 6: Get User Location ----")
    if user_id_1:
        get_location(user_id_1)

    # Test Case 7: Attempt to Get Location for Non-existent User
    print("\n---- Test Case 7: Attempt to Get Location for Non-existent User ----")
    get_location(9999)

    # Test Case 8: Create Location Share Request
    print("\n---- Test Case 8: Create Location Share Request ----")
    if user_id_1 and user_id_2:
        update_location_share(follower_id=user_id_2, following_id=user_id_1)

    # Test Case 9: Approve Location Share Request
    print("\n---- Test Case 9: Approve Location Share Request ----")
    if user_id_1 and user_id_2:
        update_location_share(follower_id=user_id_2, following_id=user_id_1, is_approved=True)

    # Test Case 10: Attempt to Follow Self
    print("\n---- Test Case 10: Attempt to Follow Self ----")
    if user_id_1:
        update_location_share(follower_id=user_id_1, following_id=user_id_1)

    # Test Case 11: Get All Users
    print("\n---- Test Case 11: Get All Users ----")
    get_users()

    # Test Case 12: Get All Location Shares
    print("\n---- Test Case 12: Get All Location Shares ----")
    get_location_shares()

    # Test Case 13: Missing Required Fields
    print("\n---- Test Case 13: Missing Required Fields ----")
    create_user("", "", "")
    add_or_update_location(None, None, None)
    update_location_share(None, None)

    # Test Case 14: Invalid Data Types
    print("\n---- Test Case 14: Invalid Data Types ----")
    add_or_update_location("invalid_user_id", "invalid_latitude", "invalid_longitude")
    update_location_share("invalid_follower_id", "invalid_following_id", "invalid_is_approved")

    # Test Case 15: Duplicate Location Share
    print("\n---- Test Case 15: Duplicate Location Share ----")
    if user_id_1 and user_id_2:
        update_location_share(follower_id=user_id_2, following_id=user_id_1)

    print("\n---- API Tests Completed ----")

if __name__ == "__main__":
    main()

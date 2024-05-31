import requests
import re
import time
from colorama import init, Fore

init(autoreset=True)

def sanitize_roblosecurity_cookie(cookie):
    warning_pattern = r"(_\|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.\|_)?"
    if not re.search(warning_pattern, cookie):
        cookie = f"_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_{cookie.strip()}"
    return cookie.strip()

def get_authenticated_user_info(session):
    url = "https://users.roblox.com/v1/users/authenticated"
    response = session.get(url)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Body: {response.text}\n")
    
    if response.status_code == 200:
        user_info = response.json()
        print(f"Authenticated User Info: {user_info}")
        return user_info, True
    else:
        return None, False

def get_csrf_token(session):
    url = "https://auth.roblox.com/v2/logout"
    response = session.post(url)
    print(f"CSRF Token Fetch Response Status: {response.status_code}")
    print(f"CSRF Token Fetch Response Headers: {response.headers}")
    
    csrf_token = response.headers.get('x-csrf-token')
    if csrf_token:
        return csrf_token
    else:
        raise Exception("Failed to fetch CSRF token")

def get_following_users(session, user_id):
    headers = {
        "accept": "application/json, text/plain, */*"
    }

    following_users = []
    next_page_cursor = ''
    
    while next_page_cursor is not None:
        url = f"https://friends.roblox.com/v1/users/{user_id}/followings?cursor={next_page_cursor}&limit=100&sortOrder=Desc"
        response = session.get(url, headers=headers)
        
        print(f"Following Users Fetch Response Status: {response.status_code}")
        print(f"Following Users Fetch Response Headers: {response.headers}")
        print(f"Following Users Fetch Response Body: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            following_users.extend(response_data['data'])
            next_page_cursor = response_data.get('nextPageCursor', None)
        else:
            print(f"Failed to fetch following users: {response.status_code} - {response.text}")
            return None
    
    print(f"Total users followed: {len(following_users)}")
    return following_users

def unfollow_users(following_users, session, csrf_token):
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "x-csrf-token": csrf_token
    }

    for user in following_users:
        user_id = user['id']
        url = f"https://friends.roblox.com/v1/users/{user_id}/unfollow"
        
        data = {"targetUserId": user_id}
        
        response = session.post(url, headers=headers, json=data)
        
        if response.status_code == 403 and 'x-csrf-token' in response.headers:
            csrf_token = response.headers['x-csrf-token']
            headers["x-csrf-token"] = csrf_token
            response = session.post(url, headers=headers, json=data)
        
        print(f"Unfollow Request Headers: {headers}")
        print(f"Unfollow Request Data: {data}")
        print(f"Unfollow Response Status: {response.status_code}")
        print(f"Unfollow Response Text: {response.text}")
        
        if response.status_code == 200:
            print(f"Successfully unfollowed user with ID {user_id}")
        else:
            print(f"Failed to unfollow user with ID {user_id}: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print(Fore.GREEN + "Please enter your .ROBLOSECURITY token (everything, even the warning).")
    print(Fore.GREEN + "Note: This token is never sent to any third party and is only used to interact with official Roblox APIs.")
    print(Fore.GREEN + "The token is forgotten once the operation is complete. Never share this token with anybody.")
    
    roblosecurity_cookie = input(Fore.BLUE + "Enter your .ROBLOSECURITY token: ")
    
    sanitized_cookie = sanitize_roblosecurity_cookie(roblosecurity_cookie)
    
    session = requests.Session()
    session.cookies.set(".ROBLOSECURITY", sanitized_cookie)
    
    try:
        user_info, success = get_authenticated_user_info(session)
        if success:
            print(f"Hello, {user_info['displayName']}")
            
            time.sleep(3)  # 3-second delay before continuing
            
            csrf_token = get_csrf_token(session)
            
            following_users = get_following_users(session, user_info['id'])
            if following_users:
                print(f"Found {len(following_users)} users to unfollow")
                unfollow_users(following_users, session, csrf_token)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

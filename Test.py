import pytz
import requests
import datetime
from pathlib import Path

import csv


# Sofia Bulgaria timezone
eet_timezone = pytz.timezone('Europe/Bucharest')

# Okta API endpoint and API token
okta_api_base_url = 'https://example.okta.com/api/v1'
api_token = 'TOKEN'

# Define the target app and team
target_app_id = 'test-app'
ignored_team = 'test-team'

# Calculate the date 30 days ago
current_time = datetime.datetime.now(eet_timezone)
thirty_days_ago = current_time - datetime.timedelta(days=30)

# Retrieve the users assigned with "test-app"
def get_users_assigned_to_app():
    url = f"{okta_api_base_url}/apps/{target_app_id}/users"
    headers = {
        'Authorization': f"SSWS {api_token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()
    
# Create a CSV export
csv_file = open('App_Removed_users.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)

# Define the fileds in the CSV
csv_writer.writerow(['User ID', 'Last Login Date', 'User Team'])

# Unassign the app from a user
def unassign_app_from_user(user_id):
    url = f"{okta_api_base_url}/users/{user_id}/roles/{target_app_id}"
    headers = {
        'Authorization': f"SSWS {api_token}"
    }
    response = requests.delete(url, headers=headers)
    return response.status_code

# Cycle the users and do the tasks
users = get_users_assigned_to_app()
affected_users = []

for user in users:
    user_id = user['id']
    last_login = user['lastLogin']
    user_team = user['profile']['user.Team']

    if last_login and last_login < thirty_days_ago and user_team != ignored_team:
        status_code = unassign_app_from_user(user_id)
        if status_code == 204: #(if request succesfull)
            affected_users.append([user_id, last_login, user_team])

csv_writer.writerows(affected_users)
csv_file.close()




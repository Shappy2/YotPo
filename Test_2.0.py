import requests
import datetime
import pytz
import csv

# Set the Sofia time zone
eet_timezone = pytz.timezone('Europe/Bucharest')

# Define domain and api token
okta_api_base_url = 'https://example.okta.com/api/v1'
api_token = 'TOKEN'

# Define the target app and team
target_app_id = 'test-app'
ignored_team = 'test-team'

# Calculate the date 30 days ago
current_time = datetime.datetime.now(eet_timezone)
thirty_days_ago = current_time - datetime.timedelta(days=30)

# Get all users assigned with test_app
def get_all_users_assigned_to_app():
    all_users = []

    # Initial request to get the first page of users
    url = f"{okta_api_base_url}/apps/{target_app_id}/users"
    headers = {
        'Authorization': f"SSWS {api_token}"
    }
    while url:
        response = requests.get(url, headers=headers)
        data = response.json()
        all_users.extend(data)
        url = response.headers.get('Link')
        if url:
            url = url.split(';')[0].strip('<').strip('>')
    
    return all_users

# Delete app from user
def unassign_app_from_user(user_id):
    url = f"{okta_api_base_url}/users/{user_id}/roles/{target_app_id}"
    headers = {
        'Authorization': f"SSWS {api_token}"
    }
    response = requests.delete(url, headers=headers)
    return response.status_code

# Create a CSV file export
csv_file = open('Export_unassigned_users.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)

# Add the columns
csv_writer.writerow(['User ID', 'Last Login Date', 'User Team'])

# Process the user data
users = get_all_users_assigned_to_app()
affected_users = []

for user in users:
    user_id = user['id']
    last_login = user['lastLogin']
    user_team = user['profile']['user.Team']

    if last_login and last_login < thirty_days_ago and user_team != ignored_team:
        status_code = unassign_app_from_user(user_id)
        if status_code == 204: #(204 is the code for succesfull operation)
            affected_users.append([user_id, last_login, user_team])

# Write the CSV file
csv_writer.writerows(affected_users)
csv_file.close()


import upstox_client
from upstox_client.rest import ApiException

# Configure the API client
api_instance = upstox_client.LoginApi()

# Your Access Token is: eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI0TkNXMjgiLCJqdGkiOiI2OTE0OWYxYmI1OWI0OTY0ODA2ZDg3NDAiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2Mjk1OTEzMSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYyOTg0ODAwfQ.qUZBsBEp6IdUH_kLuPR2NYJlvkKDdMCn_OjP90Xgs60
# # Define your app details
api_version = '2.0'
code = '60OjyA'
client_id = 'b22d7a9b-febb-42c6-b9f7-af1fb406755e'
client_secret = '2wzvinibch'
redirect_uri = 'http://localhost'
grant_type = 'authorization_code'

try:
    # Get the access token
    api_response = api_instance.token(api_version,
                                      code=code,
                                      client_id=client_id,
                                      client_secret=client_secret,
                                      redirect_uri=redirect_uri,
                                      grant_type=grant_type)

    access_token = api_response.access_token
    print(f"Your Access Token is: {access_token}")

except ApiException as e:
    print(f"Exception when calling LoginApi->token: {e}")


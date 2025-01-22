import base64
import urllib.parse
import requests
import logging


# TODO: Předělat pomocí https://oauthapi3.docs.apiary.io/
# https://developers.keboola.com/extend/common-interface/oauth/


TOKEN_URL = "https://auth.franconnectuat.net/userauth/oauth/token?X-TenantID={X_TENANT_ID}"
REFRESH_TOKEN_URL = "https://auth.franconnect.net/userauth/oauth/token?grant_type=refresh_token&refresh_token={REFRESH_TOKEN}" # noqa E501


class FranconnectTokenAPIClientException(Exception):
    pass


class FranconnectTokenAPIClient:
    def __init__(self, xtenantid, client_id, client_secret):
        self.xtenantid = xtenantid
        self.client_id = client_id
        self.client_secret = client_secret

        auth_str = f"{self.client_id}:{self.client_secret}"
        self.auth_b64 = base64.b64encode(auth_str.encode()).decode()

    def generate_access_token(self):
        token_url = TOKEN_URL.replace("{X_TENANT_ID}", f"{self.xtenantid}")

        headers = {
            'Accept': "application/json",
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': f"Basic {self.auth_b64}",
        }

        payload = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        encoded_payload = urllib.parse.urlencode(payload)

        try:
            response = requests.post(
                token_url,
                headers=headers,
                data=encoded_payload
            )
            response.raise_for_status()
            response_data = response.json()

            access_token = response_data.get("access_token")
            refresh_token = response_data.get("refresh_token")

            logging.info("Access token generated successfully")
            return access_token, refresh_token

        except requests.exceptions.RequestException as e:
            raise FranconnectTokenAPIClientException(f"Error generating access token: {e}")

    def refresh_access_token(self, old_refresh_token):
        refresh_token_url = REFRESH_TOKEN_URL.replace("{REFRESH_TOKEN}", old_refresh_token)
        headers = {
            'accept': "application/json",
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-TenantID': f"{self.xtenantid}",
            'client_id': f"{self.client_id}",
            'client_secret': f"{self.client_secret}"
        }

        try:
            response = self.post_raw(
                endpoint_path=refresh_token_url,
                headers=headers,
                is_absolute_path=True
            )
            response.raise_for_status()
            response_data = response.json()

            access_token = response_data.get("access_token")
            refresh_token = response_data.get("refresh_token")

            return access_token, refresh_token

        except Exception as e:
            raise FranconnectTokenAPIClientException(f"Error refreshing access token: {e}")

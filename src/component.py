"""
Template Component main class.

"""
import json
import logging

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

from client.token_api import FranconnectTokenAPIClient
from client.info_manager_api import InfoManagerAPIClient
from configuration import Configuration


KEY_CREDENTIALS = 'credentials'
KEY_RETRIEVE_SETTINGS = 'retrieveSettings'
REQUIRED_PARAMETERS = []


class Component(ComponentBase):
    def __init__(self):
        super().__init__()

        self.validate_configuration_parameters(REQUIRED_PARAMETERS)

        parameters = self.configuration.parameters
        self.user_credentials = parameters.get(KEY_CREDENTIALS, {})
        self.retrieve_settings = parameters.get(KEY_RETRIEVE_SETTINGS, {})

    def run(self):
        """
        Main execution code
        """
        params = Configuration(**self.configuration.parameters) # noqa F841
        self._init_clients()
        # TODO: dodělat run metodu

    def _init_clients(self):
        x_tenant_id = self.user_credentials.get('xTenantId')
        login = self.user_credentials.get('login')
        client_secret = self.user_credentials.get('clientSecret')
        token_client = FranconnectTokenAPIClient(login, x_tenant_id, client_secret)

        authorization = self.configuration.config_data["authorization"]
        authorization_credentials = authorization["oauth_api"]["credentials"]

        if not authorization.get("oauth_api"):
            new_access_token, new_refresh_token = token_client.generate_access_token()
            self.write_state_file({
                "#refresh_token": new_refresh_token,
                "auth_id": authorization_credentials.get("id", "")
            })
            self.retrieve_client = InfoManagerAPIClient(x_tenant_id, new_access_token)

        else:
            encrypted_data = json.loads(authorization_credentials["#data"])
            state_file = self.get_state_file()
            refresh_token_from_state_file = state_file.get("#refresh_token")
            auth_id = state_file.get("auth_id")

            refresh_token = self._set_refresh_token(
                auth_id,
                refresh_token_from_state_file,
                encrypted_data,
                authorization_credentials
            )
            updated_access_token, updated_refresh_token = token_client.refresh_access_token(refresh_token)
            self.write_state_file({
                "#refresh_token": updated_refresh_token,
                "auth_id": authorization_credentials.get("id", "")
            })
            self.retrieve_client = InfoManagerAPIClient(x_tenant_id, updated_access_token)

    @staticmethod
    def _set_refresh_token(auth_id, refresh_token, encrypted_data, credentials):
        if not auth_id and refresh_token:
            logging.info("Refresh token loaded from state file")

        elif refresh_token and auth_id == credentials.get("id", ""):
            logging.info("Refresh token loaded from state file")

        else:
            refresh_token = encrypted_data["refresh_token"]
            logging.info("Refresh token loaded from encrypted data")

        return refresh_token


if __name__ == "__main__":
    try:
        comp = Component()
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)

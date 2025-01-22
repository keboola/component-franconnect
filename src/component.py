"""
Template Component main class.

"""
import json  # noqa F401
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

        params = Configuration(**self.configuration.parameters)
        self.user_credentials = params.credentials
        self.retrieve_settings = params.retrieve_settings

    def run(self) -> None:
        """
        Main execution code
        """
        self._init_clients()

        try:
            response = self.retrieve_client.get_data_from_retrive_endpoint(
                module=self.retrieve_settings.module,
                sub_module=self.retrieve_settings.sub_module,
                xml_filter=self.retrieve_settings.filter_xml
            )
            logging.info(f"Data loaded from API: {response}")

        except Exception as exc:
            UserException(f"Error loading data from API: {exc}")

    def _init_clients(self) -> None:
        x_tenant_id = self.user_credentials.x_tenant_id
        client_id = self.user_credentials.client_id
        client_secret = self.user_credentials.client_secret
        token_client = FranconnectTokenAPIClient(x_tenant_id, client_id, client_secret)
        new_access_token, new_refresh_token = token_client.generate_access_token()
        self.write_state_file({
            "#refresh_token": new_refresh_token
        })
        self.retrieve_client = InfoManagerAPIClient(x_tenant_id, new_access_token)


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

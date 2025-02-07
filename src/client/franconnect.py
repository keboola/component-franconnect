import base64
from keboola.http_client import HttpClient
from keboola.component.exceptions import UserException

MODULES_ENDPOINT = "fc/rest/dataservices/module"
SUBMODULES_ENDPOINT = "fc/rest/dataservices/submodule"
RETRIEVE_ENDPOINT = "fc/rest/dataservices/retrieve"

BATCHE_SIZE = 100


class FranConnectClient(HttpClient):

    def __init__(self, tenant_id, client_id, client_secret):
        super().__init__(base_url=f"https://{tenant_id}")
        token = self.get_auth_token(tenant_id, client_id, client_secret)
        self.update_auth_header({"Authorization": f"Bearer {token}"})

    def get_auth_token(self, tenant_id: str, client_id: str, client_secret: str):
        auth_str = f"{client_id}:{client_secret}"
        basic_auth = base64.b64encode(auth_str.encode()).decode()
        headers = {"Authorization": f"Basic {basic_auth}"}

        response = self.post(
            endpoint_path="https://auth.franconnectuat.net/userauth/oauth/token",
            headers=headers,
            data={"grant_type": "client_credentials", "X-TenantID": tenant_id},
            is_absolute_path=True
        )

        return response["access_token"]

    def get_modules(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        response = self.post(endpoint_path=MODULES_ENDPOINT, headers=headers, data={"responseType": "JSON"})
        return response

    def get_submodules(self, module: str):
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        response = self.post(endpoint_path=SUBMODULES_ENDPOINT, headers=headers,
                             data={"responseType": "JSON", "module": module})
        return response

    def get_data_from_retrive_endpoint(self, module: str, sub_module: str, xml_filter: str):
        offset = 0
        while True:
            data = {
                "module": module,
                "subModule": sub_module,
                "filterXML": xml_filter,
                "limit": BATCHE_SIZE,
                "offset": offset,
                "responseType": "JSON"
            }

            response = self.post(
                endpoint_path=RETRIEVE_ENDPOINT,
                data=data
            )

            if response.get("fcResponse", {}).get("responseStatus") != "Success":
                raise UserException(f"Failed to retrieve data: {response.get('fcResponse', {}).get('error', {}).get('errorDetails')}")

            try:
                response_data = response.get("fcResponse", {}).get("responseData", {}).popitem()[1]

                if isinstance(response_data, dict):
                    response_data = [response_data]

                for record in response_data:
                    yield record

                if response.get("fcResponse", {}).get("pagination", {}).get("hasMoreRecords") == "false":
                    break

                offset += BATCHE_SIZE

            except KeyError as e:
                raise Exception(f"No data returned: {e}")

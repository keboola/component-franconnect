from keboola.http_client import HttpClient


RETRIEVE_ENDPOINT = "/rest/dataservices/retrieve"


class InfoManagerAPIClientException(Exception):
    pass


class InfoManagerAPIClient(HttpClient):
    def __init__(self, x_tenant_id, access_token):
        self.x_tenant_id = x_tenant_id
        self.token = access_token
        self.base_url = "https://" + self.x_tenant_id

    def get_data_from_retrive_endpoint(self, **kwargs):
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "module": kwargs.get('module'),
            "subModule": kwargs.get('sub_module'),
            "filterXML": kwargs.get('xml_filter'),
            "responseType": "JSON"
        }

        try:
            response = self.post_raw(
                endpoint_path=RETRIEVE_ENDPOINT,
                headers=headers,
                data=payload,
                is_absolute_path=False
            )
            response.raise_for_status()
            response_data = response.json()
            return response_data

        except Exception as e:
            raise InfoManagerAPIClientException(f"Error loading data from Info Manager API: {e}")

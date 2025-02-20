"""
Template Component main class.

"""
import logging

from keboola.component.base import ComponentBase, sync_action
from keboola.component.exceptions import UserException
from keboola.component.sync_actions import SelectElement
from keboola.csvwriter import ElasticDictWriter
from requests import HTTPError

from client.franconnect import FranConnectClient
from configuration import Configuration


class Component(ComponentBase):
    def __init__(self):
        super().__init__()
        self.params = Configuration(**self.configuration.parameters)
        self.client = None

    def run(self) -> None:
        """
        Main execution code
        """
        self.init_client()

        try:
            endpoint_data = self.client.get_data_from_retrive_endpoint(
                module=self.params.source.module,
                sub_module=self.params.source.sub_module,
                xml_filter=self.params.source.filter_xml
            )

            table_name = self.params.destination.table_name or (f"{self.params.source.module}"
                                                                f"_{self.params.source.sub_module}")

            out_table = self.create_out_table_definition(f"{table_name}.csv", has_header=True)

            writer = ElasticDictWriter(out_table.full_path, [])

            for row in endpoint_data:
                if self.params.source.module == "fim" and self.params.source.sub_module == "agreement":
                    flattened_row = {}
                    for key, value in row.items():
                        if isinstance(value, dict):
                            for nested_key, nested_value in value.items():
                                flattened_row[f"{nested_key}"] = nested_value
                        else:
                            flattened_row[key] = value
                    writer.writerow(flattened_row)
                else:
                    writer.writerow(row)

            writer.writeheader()
            writer.close()
            out_table.schema = writer.fieldnames
            self.write_manifest(out_table)

        except Exception as e:
            raise UserException(f"Error downloading the endpoint: {e}")

    def init_client(self):
        self.client = FranConnectClient(self.params.credentials.tenant_id, self.params.credentials.client_id,
                                        self.params.credentials.client_secret)

    @sync_action("testConnection")
    def test_connection(self):
        try:
            self.init_client()
        except HTTPError as e:
            raise UserException(f"Connection failed: {e.response.text}")

    @sync_action("list_modules")
    def list_modules(self):
        self.init_client()
        response = self.client.get_modules()
        modules = response.get("fcResponse", {}).get("responseData", {}).get("fcRequest", {})
        return [SelectElement(value, label) for value, label in modules.items()]

    @sync_action("list_submodules")
    def list_submodules(self):
        self.init_client()
        response = self.client.get_submodules(self.params.source.module)
        submodules = response.get("fcResponse", {}).get("responseData", {}).get("fcRequest", {})
        return [SelectElement(value, label) for value, label in submodules.items()]


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

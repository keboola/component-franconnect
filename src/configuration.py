from pydantic import BaseModel, Field, ValidationError
from keboola.component.exceptions import UserException


class Credentials(BaseModel):
    x_tenant_id: str = Field(alias="xTenantId")
    client_id: str = Field(alias="clientId")
    client_secret: str = Field(alias="#clientSecret")


class RetrieveSettings(BaseModel):
    module: str
    sub_module: str = Field(alias="subModule")
    filter_xml: str = Field(alias="filterXML")


class Configuration(BaseModel):
    debug: bool = Field(title="Debug mode", default=False)
    credentials: Credentials
    retrieve_settings: RetrieveSettings = Field(alias="retrieveSettings")

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise UserException(f"Validation Error: {', '.join(error_messages)}")

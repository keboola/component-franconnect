from pydantic import BaseModel, Field, ValidationError, field_validator
from keboola.component.exceptions import UserException


class Credentials(BaseModel):
    x_tenant_id: str = Field(alias="xTenantId")
    username: str
    password: str = Field(alias="#password")
    client_secret: str = Field(alias="clientSecret")


class RetrieveSettings(BaseModel):
    module: str
    sub_module: str = Field(alias="subModule")
    filter_xml: str = Field(alias="filterXML")


class Configuration(BaseModel):
    credentials: Credentials
    retrieve_settings: RetrieveSettings = Field(alias="retrieveSettings")

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise UserException(f"Validation Error: {', '.join(error_messages)}")

    @field_validator('credentials')
    def validate_credentials(cls, v):
        if not v.x_tenant_id or not v.username or not v.password or not v.client_secret:
            raise UserException('All credentials fields must be provided')
        return v

    @field_validator('retrieve_settings')
    def validate_retrieve_settings(cls, v):
        if not v.module or not v.sub_module or not v.filter_xml:
            raise UserException('All retrieve settings fields must be provided')
        return v

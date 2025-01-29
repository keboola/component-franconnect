from enum import Enum
from pydantic import BaseModel, Field, ValidationError, computed_field
from keboola.component.exceptions import UserException


class LoadType(str, Enum):
    full_load = "full_load"
    incremental_load = "incremental_load"


class Credentials(BaseModel):
    tenant_id: str = Field()
    client_id: str = Field()
    client_secret: str = Field(alias="#client_secret")


class Source(BaseModel):
    module: str
    sub_module: str = Field()
    filter_xml: str = Field()


class Destination(BaseModel):
    table_name: str = Field(default=None)
    load_type: LoadType = Field(default=LoadType.incremental_load)

    @computed_field
    def incremental(self) -> bool:
        return self.load_type == LoadType.incremental_load


class Configuration(BaseModel):
    credentials: Credentials
    source: Source
    destination: Destination
    debug: bool = Field(title="Debug mode", default=False)

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise UserException(f"Validation Error: {', '.join(error_messages)}")

component-franconnect
=============

A Keboola component for integrating with FranConnect, providing access to various modules and sub-modules with configurable data loading options.

Prerequisites
=============

To use this component, you will need:
- FranConnect tenant ID
- Client ID
- Client Secret

Configuration - component configuration level:
=============
## Credentials
- tenant_id (Required) - Your FranConnect tenant identifier
- client_id (Required) - OAuth client ID
- client_secret (Required) - OAuth client secret (stored securely)

Configuration - configuration row level:
=============

## Source Configuration
- module (Required) - The main module to extract data from
- sub_module (Required) - Specific sub-module within the main module
- filter_xml (Required) - XML filter to apply to the data extraction

## Destination Configuration
- table_name - Name of the output table in Keboola
- load_type - Type of load: "full_load" or "incremental_load"

## Additional Settings
- debug - Enable debug mode for troubleshooting (Default: false)

Param 2
-------

```json
{
  "credentials": {
    "tenant_id": "your-tenant-id",
    "client_id": "your-client-id",
    "#client_secret": "your-client-secret"
  },
  "source": {
    "module": "example-module",
    "sub_module": "example-sub-module",
    "filter_xml": "<filter></filter>"
  },
  "destination": {
    "table_name": "my_output_table",
    "load_type": "incremental_load"
  },
  "debug": false
}
```

Development
-----------

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to
your custom path in the `docker-compose.yml` file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository, init the workspace and run the component with following
command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
git clone https://github.com/keboola/componet-franconnect componet_franconnect
cd componet_franconnect
docker-compose build
docker-compose run --rm dev
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the test suite and lint check using this command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose run --rm test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration
===========

For information about deployment and integration with KBC, please refer to the
[deployment section of developers
documentation](https://developers.keboola.com/extend/component/deployment/)

from urllib import request
from yaml import load

from yaml import Loader


def parse_openapi(definition: str, location_type: str):
    """
    Takes an OpenAPI definition in YAML and returns it as a dictionary, with
    endpoints grouped by tags.

      Parameters:
        definition (str): The path to the definition file (either local or hosted)
        location_type (str): Definition file location type (either 'url' or 'file')

      Returns:
        dict: A dictionary of tags, each tag containing a list of API endpoints (as dicts)

      Example:

        info:
          version: 2.0.0
        openapi: 3.0.0
        paths:
          /account/op-create_authorisation_token:
            post:
              description: Create an authorisation OAuth token and OAuth consumer.
              operationId: AccountHandler_create_authorisation_token
              responses:
                '200':
                  content:
                    application/json:
                      schema:
                        additionalProperties: true
                        type: object
                  description: 'A JSON object containing: ``token_key``, ``token_secret``,
                    ``consumer_key``, and ``name``.'
              summary: Create an authorisation token
              tags:
              - Logged-in user


      will return as:

        {
          "Logged-in user": [
            {
              "/account/op-create_authorisation_token": {
                "post": {
                  "description": "Create an authorisation OAuth token and OAuth consumer.",
                  "operationId": "AccountHandler_create_authorisation_token",
                  "responses": {
                    "200": {
                      "content": {
                        "application/json": {
                          "schema": {
                            "additionalProperties": true,
                            "type": "object"
                          }
                        }
                      },
                      "description": "A JSON object containing: ``token_key``, ``token_secret``, ``consumer_key``, and ``name``."
                    }
                  },
                  "summary": "Create an authorisation token",
                  "tags": [
                    "Logged-in user"
                  ]
                }
              }
            }
          ]
        }
    """
    if location_type == "file":
        definition = request.urlopen(definition)
    elif location_type == "url":
        definition = open(definition)
    else:
        raise ValueError("Arg 'type' must be either 'file' or 'url'")
    loaded_definition = load(definition, Loader)
    tagged_definition = {}

    for endpoint in loaded_definition["paths"]:
        for method in loaded_definition["paths"][endpoint]:
            if method != "parameters":
                tag = loaded_definition["paths"][endpoint][method]["tags"][0]
                if tag in tagged_definition:
                    if {
                        endpoint: loaded_definition["paths"][endpoint]
                    } not in tagged_definition[tag]:
                        tagged_definition[tag] = [
                            *tagged_definition[tag],
                            {endpoint: loaded_definition["paths"][endpoint]},
                        ]
                else:
                    tagged_definition[tag] = [
                        {endpoint: loaded_definition["paths"][endpoint]}
                    ]

    return tagged_definition

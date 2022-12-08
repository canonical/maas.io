from urllib import request
from yaml import load

from yaml import Loader


def parse_openapi(definition: str, location_type: str):
    """
    Takes an OpenAPI definition in YAML and returns it as a dictionary, with
    endpoints grouped by tags.

      Parameters:
        definition (str): The path to the definition file (local or hosted)
        location_type (str): Definition file location type ('url' or 'file')

      Returns:
        dict: A dictionary of tags, each tag containing a list of API 
        endpoints (as dicts)
    """
    if location_type == "url":
        definition = request.urlopen(definition)
    elif location_type == "file":
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

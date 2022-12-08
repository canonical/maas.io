from collections import defaultdict
from yaml import load
from yaml import Loader


def parse_openapi(definition: str, location_type: str, session):
    """
    Takes an OpenAPI definition in YAML and returns it as a dictionary, with
    endpoints grouped by tags.

      Parameters:
        definition (str): The path to the definition file (local or hosted)
        location_type (str): Definition file location type ('url' or 'file')
        session: Session from talisker.requests.get_sesssion()

      Returns:
        dict: A dictionary of tags, each tag containing a list of API
        endpoints (as dicts)
    """
    if location_type == "url":
        definition = session.get(definition).text
    elif location_type == "file":
        definition = open(definition)
    else:
        raise ValueError("Arg 'type' must be either 'file' or 'url'")
    loaded_definition = load(definition, Loader)

    tagged_definition = defaultdict(list)

    for endpoint, methods in loaded_definition["paths"].items():
        for method, definition in methods.items():
            if method != "parameters":
                tag = definition["tags"][0]
                if {endpoint: methods} not in tagged_definition[tag]:
                    tagged_definition[tag].append({endpoint: methods})

    return tagged_definition

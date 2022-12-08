from collections import defaultdict
from yaml import load
from yaml import Loader


def parse_openapi(definition):
    """
    Takes an OpenAPI definition in YAML and returns it as a dictionary, with
    endpoints grouped by tags.

      Parameters:
        definition: The OpenAPI YAML defintion (loaded from file or URL)

      Returns:
        dict: A dictionary of tags, each tag containing a list of API
        endpoints (as dicts)
    """
    loaded_definition = load(definition, Loader)

    tagged_definition = defaultdict(list)

    for endpoint, methods in loaded_definition["paths"].items():
        for method, definition in methods.items():
            if method != "parameters":
                tag = definition["tags"][0]
                if {endpoint: methods} not in tagged_definition[tag]:
                    tagged_definition[tag].append({endpoint: methods})

    return tagged_definition


def read_yaml_from_url(url: str, session):
    return session.get(url).text


def read_yaml_from_file(filename: str):
    return open(filename)

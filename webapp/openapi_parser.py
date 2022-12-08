from urllib import request
from yaml import load

from yaml import Loader


def parse_openapi(url: str):
    definition = request.urlopen(url)
    loaded_definition = load(definition, Loader)
    tagged_definition = {}

    for endpoint, method in loaded_definition["paths"].items():
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

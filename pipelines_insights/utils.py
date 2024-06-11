from pathlib import Path
from typing import List, Set

import yaml
from yaml import SafeLoader


def basic_equals(obj1, obj2):
    """Check if objects are the same class and the attributes are equals"""
    return obj1.__class__ == obj2.__class__ and obj1.__dict__ == obj2.__dict__


def read_yml(path: Path | str):
    with open(path, 'r') as f:
        return yaml.load(f, SafeLoader)


def enlist(_elem) -> List:
    if isinstance(_elem, (list, tuple, set)):
        return list(_elem)
    return [_elem]


def enset(_elem) -> Set:
    if isinstance(_elem, (list, tuple, set)):
        return set(_elem)
    return {_elem}

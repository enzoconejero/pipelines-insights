from pathlib import Path
from typing import List, Dict, Set

from pipelines_insights.drawer import Drawer
from pipelines_insights.utils import basic_equals, read_yml, enlist, enset


class Node:
    """Node of a Pipeline"""

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d['name'])

    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f'Node<{self.name}>'

    def __eq__(self, other):
        return basic_equals(self, other)


class Pipeline:
    """Generic pipeline with linear dependencies (no recursive)"""

    @classmethod
    def from_dict(cls, d: dict):
        return cls._parse_dict(d)

    @classmethod
    def from_yml(cls, path: Path | str):
        d = read_yml(path)
        return cls.from_dict(d)

    @classmethod
    def _parse_dict(cls, d: dict):
        to_parse_depenencies: List[Dict] = []
        nodes = []

        for node_conf in d.get('nodes', []):
            # Parse the node
            node = Node.from_dict(node_conf)
            nodes.append(node)

            # Parse dependencies defined inside the node
            to_parse_depenencies.extend([{node.name: n} for n in node_conf.get('nexts', [])])
            to_parse_depenencies.extend([{d: node.name} for d in node_conf.get('depends', [])])

        # Get dependencies under key 'dependencies' and enlist the sons
        dependencies = {k: enset(v) for k, v in d.get('dependencies', {}).items()}

        # Add the dependencies defined inside the nodes
        for dep in to_parse_depenencies:
            for parent, son in dep.items():
                if parent in dependencies:
                    dependencies[parent].add(son)
                else:
                    dependencies[parent] = {son}

        return cls(
            name=d['name'],
            nodes=nodes,
            dependencies=dependencies
        )

    def __init__(self, name: str, nodes: List[Node] = None, dependencies: Dict[str, Set[str]] = None):
        self.name: str = name
        self.nodes: List[Node] = nodes or []
        self.dependencies: Dict[str, Set[str]] = dependencies or {}
        self._map_nodes = {n.name: n for n in self.nodes}

    def __str__(self):
        return f'Pipeline<{self.name}>'

    def __eq__(self, other):
        return basic_equals(self, other)

    def draw(self):
        """Create a graph representing visually the pipeline"""
        return Drawer.from_pipeline(self).draw()

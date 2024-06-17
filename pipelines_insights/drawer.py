import os
from abc import abstractmethod
from pathlib import Path
from typing import List, Dict

from drawsvg import Drawing, Lines, Line, Rectangle, Text, Marker, DrawingElement

__all__ = ['Drawer']

LEVEL_GAP_X = 20
LEVEL_GAP_Y = 20
NODE_HEIGHT = 30

TEMPDIR = Path(__file__).parents[1] / 'temp'


class Draw:

    @abstractmethod
    def as_svg_elems(self) -> List[DrawingElement]:
        pass


class NodeRect(Draw):
    """Square with a text centered inside"""

    def __init__(self, name: str, order_y: int):
        self.name: str = name.strip()
        self.level_x: XLevel = None
        self.order_y: int = order_y

        self.nexts: List[NodeRect] = []
        self.prevs: List[NodeRect] = []
        self.x: float = 0
        self.y: float = 0

    def __str__(self):
        return f'Node<{self.name} ({self.level_x}, {self.order_y})>'

    def as_svg_elems(self) -> List[DrawingElement]:
        """Generate list of SVG elements to draw"""
        rect = Rectangle(x=self.x, y=self.y, width=self.width(), height=self.height(), fill='red')
        text = Text(self.name, 6, self.x + (self.width() - self.text_width()) / 2, self.y + self.height() / 2)
        arrs = [Arrow(*self.arrow_start(), *n.arrow_end()) for n in self.nexts]
        return [rect, text, *[a.as_svg_elems()[0] for a in arrs]]

    def width(self):
        """Full width of rect, text + border + gap"""
        return self.text_width() + 15

    def height(self):
        """Full height of rect, text + border + gap"""
        return NODE_HEIGHT

    def text_width(self):
        return len(self.name) * 6

    def arrow_start(self):
        """Point where arrow starts to dependents"""
        return self.x + self.width(), self.y + self.height() / 2

    def arrow_end(self):
        """Point wherere arrow reachs from parents"""
        return self.x, self.y + self.height() / 2

    def set_initial_position(self):
        self.x = self.level_x.x_start()
        prev_nodes = [n for n in self.level_x.nodes if n.order_y < self.order_y]
        prev_nodes_heights = sum(n.height() for n in prev_nodes)
        prev_nodes_gaps = len(prev_nodes) * LEVEL_GAP_Y
        self.y = prev_nodes_heights + prev_nodes_gaps


class Arrow(Draw):
    """Rect line with and arrow end"""

    def __init__(self, x_start: float, y_start: float, x_end: float, y_end: float):
        self.x_start: float = x_start
        self.y_start: float = y_start
        self.x_end: float = x_end
        self.y_end: float = y_end

    def __str__(self):
        return f'Arrow({self.x_start, self.y_start} -> {self.x_end, self.y_end})'

    def as_svg_elems(self) -> List[DrawingElement]:
        # TODO, consider offset to fix the end of the line is thicker than the end of the arrow
        end = Marker(-4, -2, 0, 2)
        end.append(Lines(-4, 2, 0, 0, -4, -2, fill='blue', close=True))
        return [Line(self.x_start, self.y_start, self.x_end, self.y_end, stroke='black', marker_end=end)]


class XLevel:
    """Container of the nodes of a level"""
    def __init__(self, nodes: List[NodeRect], level: int):
        self.nodes: List[NodeRect] = nodes or []
        self.level: int = level
        self.other_levels: List[XLevel] = []
        
    def max_width(self):
        return max(n.width() for n in self.nodes)
    
    def x_start(self) -> float:
        if self.level == 0:
            return 0
        
        return self.other_levels[self.level-1].x_end() + LEVEL_GAP_X
        
    def x_end(self) -> float:
        return self.x_start() + self.max_width()

    def set_initial_positions(self):
        for node in self.nodes:
            node.set_initial_position()


class Drawer:
    """Class that draws the pipeline as SVG"""

    @classmethod
    def from_pipeline(cls, pipeline):
        from pipelines_insights.pipelines import Pipeline
        pipeline: Pipeline = pipeline

        _nodes_to_level = {n.name for n in pipeline.nodes}
        _leveled_nodes = set()

        dependents = set()
        for dep in pipeline.dependencies.values():
            dependents = dependents.union(dep)

        # All the independent nodes are level 0
        levels = [_nodes_to_level - dependents]
        _nodes_to_level -= levels[0]

        while _nodes_to_level:
            # All the nodes wich parents are already leveled
            in_level = set()
            for node in _nodes_to_level:
                parents = {k for k, v in pipeline.dependencies.items() if node in v}
                not_leveled_parents = parents.intersection(_nodes_to_level)
                if not not_leveled_parents:
                    in_level.add(node)

            _nodes_to_level -= in_level
            levels.append(in_level)

        # Convert sets to sorted list
        sorted_levels = [sorted(lv) for lv in levels]
        sorted_deps = {k: sorted(v) for k, v in pipeline.dependencies.items()}

        print(levels, sep='\n')
        return Drawer(sorted_levels, sorted_deps).draw()

    def __init__(self, levels: List[List[str]], dependencies: Dict[str, List[str]]):
        self.levels: List[List[str]] = levels
        self.dependencies: Dict[str, List[str]] = dependencies  # k needs v
        
        self.draws = []

    def draw(self):
        # TODO sort modes
        _map = dict()
        levels = []
        
        # Instance levels
        for x, nodes in enumerate(self.levels):
            nodes_in_level = []
            
            for y, node in enumerate(nodes):
                svg = NodeRect(node, order_y=y)
                _map[node] = svg
                nodes_in_level.append(svg)
            
            level = XLevel(nodes_in_level, x)
            levels.append(level)
            for node in nodes_in_level:
                node.level_x = level

        # Set reference to other levels
        for level in levels:
            level.other_levels = levels
        
        # Set the references to dependencies inside the DrawNodes
        for parent, sons in self.dependencies.items():
            _map[parent].nexts = [_map[s] for s in sons]
            for son in sons:
                _map[son].prevs.append(_map[parent])

        # Set initials positions
        for level in levels:
            level.set_initial_positions()

        # Draw
        # for level in self.levels:
        for level in levels:
            for node in level.nodes:
                self.draws.extend(node.as_svg_elems())

        canvas = Drawing(600, 300, style='background-color: #dedede')
        canvas.extend(self.draws)
        os.makedirs(TEMPDIR, exist_ok=True)
        canvas.save_html(TEMPDIR / 'draw.html')
        return self

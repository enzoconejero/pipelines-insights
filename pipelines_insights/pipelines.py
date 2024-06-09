from pipelines_insights.utils import basic_equals


class Pipeline:
    """Generic pipeline"""

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            name=d['name'],
        )

    def __init__(self, name: str):
        self.name: str = name

    def __eq__(self, other):
        return basic_equals(self, other)

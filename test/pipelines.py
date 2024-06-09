# Dummy test
from pipelines_insights.pipelines import Pipeline


def test_dummy():
    assert True


def test_open_from_dict():
    p1 = Pipeline.from_dict({'name': 'pipe'})
    p2 = Pipeline('pipe')
    assert p1 == p2

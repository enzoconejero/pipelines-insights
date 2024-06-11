# Dummy test
from pathlib import Path

from pipelines_insights.pipelines import Pipeline, Node

testdir = Path(__file__).parent
pipelinesdirs = testdir / 'pipelines'

linear = Pipeline(
    name='Linear Rutine',
    nodes=[Node('Wake up'), Node('Live'), Node('Sleep')],
    dependencies={
        'Wake Up': {'Live'},
        'Live': {'Sleep'},
    }
)


def test_dummy():
    assert True


def test_open_from_dict():
    p1 = Pipeline.from_dict({'name': 'pipe'})
    p2 = Pipeline('pipe')
    assert p1 == p2


def test_depenencies():

    # Direct
    p1 = Pipeline.from_dict({
        'name': 'pipe',
        'nodes': [{'name': 'N1'}, {'name': 'N2'}, {'name': 'N3'}],
        'dependencies': {
            'N1': 'N2',
            'N2': 'N3'
        }
    })

    # Node has dependents
    p2 = Pipeline.from_dict({
        'name': 'pipe',
        'nodes': [
            {'name': 'N1', 'nexts': ['N2']},
            {'name': 'N2', 'nexts': ['N3']},
            {'name': 'N3'}
        ],
    })

    # Node depends on
    p3 = Pipeline.from_dict({
        'name': 'pipe',
        'nodes': [
            {'name': 'N1'},
            {'name': 'N2', 'depends': ['N1']},
            {'name': 'N3', 'depends': ['N2']}
        ],
    })

    # Mixed depends & nexts
    p4 = Pipeline.from_dict({
        'name': 'pipe',
        'nodes': [
            {'name': 'N1'},
            {'name': 'N2', 'depends': ['N1'], 'nexts': ['N3']},
            {'name': 'N3'}
        ],
    })

    assert p1 == p2 == p3 == p4


def test_from_yml():
    p = Pipeline.from_yml(pipelinesdirs / 'rutine.yml')
    assert p == linear


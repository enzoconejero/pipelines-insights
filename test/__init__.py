from pathlib import Path

from pipelines_insights.pipelines import Pipeline

testdir = Path(__file__).parent
pipelinesdirs = testdir / 'pipelines'

if __name__ == '__main__':
    Pipeline.from_yml(pipelinesdirs / 'ex_1.yml').draw()

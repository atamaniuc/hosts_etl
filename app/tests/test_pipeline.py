from pipeline.etl_pipeline import ETLPipeline
from fetchers.base import BaseFetcher
from processors.base import BaseProcessor
from storage.base import BaseStorage
from visualizations.base import BaseVisualizer


class DummyFetcher(BaseFetcher):
    def __init__(self):
        super().__init__("http://dummy.com", "dummy")

    def fetch(self):
        return [{"ip": "1.1.1.1", "hostname": "h"}]


class DummyProcessor(BaseProcessor):
    def process(self, data):
        return data


class DummyStorage(BaseStorage):
    def save(self, data):
        pass


class DummyVisualizer(BaseVisualizer):
    def generate(self):
        pass


class DummyPipeline(ETLPipeline):
    def run(self):
        pass


def test_pipeline():
    pipeline = DummyPipeline(
        fetchers=[DummyFetcher()],
        processor=DummyProcessor(),
        storage=DummyStorage(),
        visualizer=DummyVisualizer(),
    )
    pipeline.run()

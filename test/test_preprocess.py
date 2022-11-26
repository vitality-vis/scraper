import pytest
import shutil
from pathlib import Path
from paperscraper._preprocess import get_unique_venues, get_extracted_data
from paperscraper.config import Config


@pytest.fixture(scope="class")
def test_config(request, tmp_path_factory):
    root_dir = Path(__file__).parent
    output_dir = tmp_path_factory.mktemp("output")
    _config = Config(root_dir=root_dir, output_dir=output_dir)
    _config.interesting_venues = {
        "Handbook of Human Computation": {
            "sourcetype": "booktitle",
            "publishers": []
        },
        "Recommender Systems Handbook": {
            "sourcetype": "booktitle",
            "publishers": []
        },
        "Handbook of Heuristics": {
            "sourcetype": "booktitle",
            "publishers": []
        }
    }
    yield _config
    shutil.rmtree(str(output_dir))


class Test_get_unique_venues:
    def test_get_unique_venues_first(self, test_config):
        result = get_unique_venues(test_config, force=True)
        _len = len(result)
        result.close(force=False)
        assert _len == 4

    def test_get_unique_venues_second(self, test_config):
        result = get_unique_venues(test_config, force=False)
        _len = len(result)
        result.close(force=False)
        assert _len == 4


class Test_get_extracted_data:
    def test_get_extracted_data_first(self, test_config):
        result = get_extracted_data(test_config, force=True)
        _len = len(result)
        result.close(force=False)
        assert _len == 6

    def test_get_extracted_data_second(self, test_config):
        result = get_extracted_data(test_config, force=False)
        _len = len(result)
        result.close(force=False)
        assert _len == 6

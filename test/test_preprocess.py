import pytest
import shutil
from pathlib import Path
from paperscraper._preprocess import get_extracted_data
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


class Test_get_extracted_data:
    def _get_extracted_data_results(self, data, venues):
        _len_data = len(data)
        data.close(force=True)
        _len_venues = len(venues)
        venues.close(force=True)
        assert _len_data == 6
        assert _len_venues == 4
    
    def test_get_extracted_data_first(self, test_config):
        data, venues = get_extracted_data(test_config, force=True)
        self._get_extracted_data_results(data, venues)

    def test_get_extracted_data_second(self, test_config):
        data, venues = get_extracted_data(test_config, force=False)
        self._get_extracted_data_results(data, venues)

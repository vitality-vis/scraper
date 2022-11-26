import pytest
import importlib
from click.testing import CliRunner
import paperscraper
import pytest_mock

import paperscraper._cli


@pytest.fixture(scope="function")
def runner():
    return CliRunner()


def called_with_config_and_force(mocked_function):
    mocked_function.assert_called_with(config=paperscraper._cli.config, force=True)


def mock_function(mocker, mock_function):
    mocker.patch(mock_function)
    # Before the main methods gets imported need to mock them
    importlib.reload(paperscraper._cli)


def test_process_db(runner, mocker):
    mock_function(mocker, "paperscraper._preprocess.get_processed_db")
    result = runner.invoke(paperscraper._cli.cli, ["process", "process-db", "-f"])
    called_with_config_and_force(paperscraper._preprocess.get_processed_db)


def test_extract_data(runner, mocker):
    mock_function(mocker, "paperscraper._preprocess.get_extracted_data")
    result = runner.invoke(paperscraper._cli.cli, ["process", "extract-data", "-f"])
    called_with_config_and_force(paperscraper._preprocess.get_extracted_data)


def test_process_data(runner, mocker):
    mock_function(mocker, "paperscraper._preprocess.get_processed_data")
    result = runner.invoke(paperscraper._cli.cli, ["process", "process-data", "-f"])
    called_with_config_and_force(paperscraper._preprocess.get_processed_data)


def test_post_process_data(runner, mocker):
    mock_function(mocker, "paperscraper._postprocess.get_post_processed_data")
    result = runner.invoke(paperscraper._cli.cli, ["process", "post-process-data", "-f"])
    called_with_config_and_force(paperscraper._postprocess.get_post_processed_data)


def test_run_all(runner, mocker):
    mock_function(mocker, "paperscraper._preprocess.get_processed_db")
    mock_function(mocker, "paperscraper._preprocess.get_extracted_data")
    mock_function(mocker, "paperscraper._preprocess.get_processed_data")
    mock_function(mocker, "paperscraper._postprocess.get_post_processed_data")
    result = runner.invoke(paperscraper._cli.cli, ["process", "run-all", "-f"])
    called_with_config_and_force(paperscraper._preprocess.get_processed_db)
    called_with_config_and_force(paperscraper._preprocess.get_extracted_data)
    called_with_config_and_force(paperscraper._preprocess.get_processed_data)
    called_with_config_and_force(paperscraper._postprocess.get_post_processed_data)

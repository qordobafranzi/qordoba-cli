import os

import pytest
from mock import MagicMock

from qordoba.commands.push import select_version_tag, select_source_columns, push_command, update_file, upload_file
from qordoba.languages import Language
from qordoba.settings import PatternNotFound
from qordoba.sources import validate_path


@pytest.fixture
def mock_api(monkeypatch):
    api_mock = MagicMock()
    monkeypatch.setattr('qordoba.commands.push.ProjectAPI', api_mock)
    return api_mock.return_value


@pytest.fixture
def mock_change_dir(monkeypatch, curdir):
    root = os.path.abspath(curdir)
    chdir_path = os.path.join(root, 'fixtures', 'push')
    monkeypatch.chdir(chdir_path)
    return chdir_path


@pytest.fixture
def mock_update(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr('qordoba.commands.push.update_file', mock)
    return mock


@pytest.fixture
def mock_upload(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr('qordoba.commands.push.upload_file', mock)
    return mock


@pytest.fixture
def lang_en_us(lang_en_data):
    return Language(lang_en_data)


def test_select_version_tag(mock_input):
    mock_input.side_effect = ('v1', 'v2')

    answer = select_version_tag('test.json', ('v1',))

    assert answer == 'v2'
    mock_input.assert_called()


def test_select_source_columns_1(mock_input):
    columns = [
        {'id': 1,
         'name': 'first_column',
         'empty': False}
    ]

    res = select_source_columns(columns)

    assert 'source_columns' in res
    assert res['source_columns'] == [1, ]
    mock_input.assert_not_called()


def test_select_source_columns_2(mock_input):
    columns = [
        {'id': 1,
         'name': 'first_column',
         'empty': False},
        {'id': 2,
         'name': 'second_column',
         'empty': False}
    ]
    mock_input.side_effect = ('1,2', 1)

    res = select_source_columns(columns)
    assert 'source_columns' in res
    assert res['source_columns'] == [1, 2]
    assert 'reference_columns' in res
    assert res['reference_columns'] is None

    mock_input.assert_called_once()


def test_select_source_columns_3(mock_input):
    columns = [
        {'id': 1,
         'name': 'first_column',
         'empty': False},
        {'id': 2,
         'name': 'second_column',
         'empty': True},
        {'id': 3,
         'name': 'reference_column',
         'empty': False}
    ]
    mock_input.side_effect = ('1', 2)

    res = select_source_columns(columns)
    assert 'source_columns' in res
    assert res['source_columns'] == [1, 3]
    assert 'reference_columns' in res
    assert res['reference_columns'] == 3

    assert mock_input.call_count == 2


def test_push_command_error(mock_api, mock_change_dir,
                            language_response,
                            project_response):
    mock_api.get_languages.return_value = language_response
    mock_api.get_project.return_value = project_response

    with pytest.raises(PatternNotFound):
        push_command(mock_change_dir, {})


def test_push_command(mock_api, mock_change_dir,
                      mock_update,
                      mock_upload,
                      language_response,
                      project_response):
    mock_api.get_languages.return_value = language_response
    mock_api.get_project.return_value = project_response
    mock_api.page_search.return_value = ()

    push_command(mock_change_dir, {}, files=(os.path.join(mock_change_dir, 'test.json'),))

    mock_update.assert_not_called()
    mock_upload.assert_called_once()


def test_push_command_update(mock_api, mock_change_dir,
                             mock_update,
                             mock_upload,
                             language_response,
                             project_response):
    mock_api.get_languages.return_value = language_response
    mock_api.get_project.return_value = project_response
    mock_api.page_search.return_value = ('test',)

    push_command(mock_change_dir, {}, update=True, files=(os.path.join(mock_change_dir, 'test.json'),))

    mock_update.assert_called_once()
    mock_upload.assert_not_called()


def test_upload_file(mock_api, mock_change_dir,
                     mock_lang_storage,
                     lang_en_us
                     ):

    mock_api.upload_anytype_file.return_value = {'upload_id': 1, 'version_tags': ['initial_value', ]}
    mock_api.append_file.return_value = {}
    path = validate_path(mock_change_dir, 'test.json', lang_en_us)

    upload_file(mock_api, path, version='v1')

    mock_api.upload_anytype_file.assert_called_once()
    mock_api.append_file.assert_called_with(1, 'test.json', version_tag='v1')

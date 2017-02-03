import json
import os
import tempfile
from argparse import ArgumentTypeError

try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

import pytest
import shutil
from mock import MagicMock
from qordoba.commands.pull import pull_command, validate_languges_input
from qordoba.languages import Language
from qordoba.project import ResponsePaginatedResult, PageStatus


@pytest.fixture
def mock_api(monkeypatch):
    api_mock = MagicMock()
    monkeypatch.setattr('qordoba.commands.pull.ProjectAPI', api_mock)
    return api_mock.return_value


@pytest.fixture
def lang_en_us(lang_en_data):
    return Language(lang_en_data)


@pytest.fixture
def lang_fr():
    return Language({
        "id": 110,
        "name": "French - France",
        "code": "fr-fr",
        "direction": "ltr",
        "override_order": "aaa - naa - French - France"
    })


@pytest.fixture
def lang_ru():
    return Language({
        "id": 190,
        "name": "Russian - Russia",
        "code": "ru-ru",
        "direction": "ltr",
        "override_order": "Russian - Russia"
    }, )


@pytest.fixture
def page_search_response(curdir):
    root = os.path.abspath(curdir)
    path = os.path.join(root, 'fixtures', 'pull', 'page_search_response.json')

    f = open(path, 'r')
    yield json.load(f)

    f.close()


@pytest.fixture
def page_details_response(curdir):
    root = os.path.abspath(curdir)
    path = os.path.join(root, 'fixtures', 'pull', 'page_details.json')

    f = open(path, 'r')
    yield json.load(f)

    f.close()


@pytest.fixture
def page_search_paginated(page_search_response):
    return ResponsePaginatedResult('pages', lambda *args, **kwargs: page_search_response, (), {})


@pytest.fixture
def mock_tmp_dir(monkeypatch):
    curdir = tempfile.mkdtemp()
    monkeypatch.chdir(curdir)
    yield curdir


@pytest.fixture
def create_test_file(mock_tmp_dir):
    with open(os.path.join(mock_tmp_dir, 'ru-ru.json'), 'w') as f:
        f.write('empty')


def test_validate_language_input(mock_lang_storage, lang_fr, lang_en_us):
    res = validate_languges_input(('fr',), (lang_fr, lang_en_us))

    assert len(res) == 1
    assert res[0] == lang_fr


def test_validate_language_input_error(mock_lang_storage, lang_fr):
    with pytest.raises(ArgumentTypeError) as e:
        validate_languges_input(('ru',), (lang_fr,))


def test_pull(mock_api, mock_tmp_dir,
              project_response,
              page_search_paginated,
              language_response,
              page_details_response,
              lang_ru):
    mock_api.get_languages.return_value = language_response
    mock_api.get_project.return_value = project_response
    mock_api.page_search.return_value = page_search_paginated
    mock_api.get_page_details.return_value = page_details_response
    mock_api.download_file.return_value.raw = StringIO(b'test')

    pull_command(mock_tmp_dir, {}, languages=('ru-ru',))

    mock_api.get_project.assert_called_once()

    mock_api.page_search.assert_called_once()
    mock_api.page_search.assert_called_with(lang_ru.id, status=[PageStatus.completed, ])

    mock_api.get_page_details.assert_called_once()
    mock_api.get_page_details.assert_called_with(lang_ru.id, page_details_response['id'])

    mock_api.download_file.assert_called_once()
    mock_api.download_file.assert_called_with(page_details_response['id'], lang_ru.id, milestone=None)

    assert os.path.exists(os.path.join(mock_tmp_dir, 'ru-ru.json'))


def test_pull_exists_skip(mock_api, mock_tmp_dir,
                     create_test_file,
                     mock_input,
                     project_response,
                     page_search_paginated,
                     language_response,
                     page_details_response,
                     lang_ru):
    mock_input.side_effect = (1, )

    mock_api.get_languages.return_value = language_response
    mock_api.get_project.return_value = project_response
    mock_api.page_search.return_value = page_search_paginated
    mock_api.get_page_details.return_value = page_details_response
    mock_api.download_file.return_value.raw = StringIO(b'test')

    pull_command(mock_tmp_dir, {}, languages=('ru-ru',))

    mock_api.get_project.assert_called_once()

    mock_api.page_search.assert_called_once()
    mock_api.page_search.assert_called_with(lang_ru.id, status=[PageStatus.completed, ])

    mock_api.get_page_details.assert_called_once()
    mock_api.get_page_details.assert_called_with(lang_ru.id, page_details_response['id'])

    mock_api.download_file.assert_not_called()

    assert os.path.exists(os.path.join(mock_tmp_dir, 'ru-ru.json'))


def test_pull_exists_replace(mock_api, mock_tmp_dir,
                     create_test_file,
                     mock_input,
                     project_response,
                     page_search_paginated,
                     language_response,
                     page_details_response,
                     lang_ru):
    mock_input.side_effect = (2, )

    mock_api.get_languages.return_value = language_response
    mock_api.get_project.return_value = project_response
    mock_api.page_search.return_value = page_search_paginated
    mock_api.get_page_details.return_value = page_details_response
    mock_api.download_file.return_value.raw = StringIO(b'test')

    pull_command(mock_tmp_dir, {}, languages=('ru-ru',))

    mock_api.get_project.assert_called_once()

    mock_api.page_search.assert_called_once()
    mock_api.page_search.assert_called_with(lang_ru.id, status=[PageStatus.completed, ])

    mock_api.get_page_details.assert_called_once()
    mock_api.get_page_details.assert_called_with(lang_ru.id, page_details_response['id'])

    mock_api.download_file.assert_called_once()
    mock_api.download_file.assert_called_with(page_details_response['id'], lang_ru.id, milestone=None)

    assert os.path.exists(os.path.join(mock_tmp_dir, 'ru-ru.json'))

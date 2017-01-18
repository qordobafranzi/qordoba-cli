import json
import os

import pytest

from mock import MagicMock

from qordoba.languages import init_language_storage


@pytest.fixture
def lang_en_data():
    return {
        "id": 94,
        "name": "English - United States",
        "code": "en-us",
        "direction": "ltr",
        "override_order": "aaa - aaa - English - United States"
    }


@pytest.fixture
def language_response(curdir):
    root = os.path.abspath(curdir)
    path = os.path.join(root, 'fixtures/languages_response.json')

    f = open(path, 'rb')
    yield json.load(f)['languages']

    f.close()


@pytest.fixture
def mock_lang_storage(language_response):
    api = MagicMock()
    api.get_languages.return_value = language_response

    init_language_storage(api)


@pytest.fixture
def project_response(curdir):
    root = os.path.abspath(curdir)
    path = os.path.join(root, 'fixtures/project_response.json')

    f = open(path, 'rb')
    yield json.load(f)['project']

    f.close()


@pytest.fixture
def curdir():
    return '.'

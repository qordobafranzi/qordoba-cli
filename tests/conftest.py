import json
import os

import pytest

from mock import MagicMock

from qordoba.languages import init_language_storage
from qordoba.settings import load_settings


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
    path = os.path.join(root, 'fixtures', 'languages_response.json')

    f = open(path, 'r')
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
    path = os.path.join(root, 'fixtures', 'project_response.json')

    f = open(path, 'r')
    yield json.load(f)['project']

    f.close()


@pytest.fixture
def page_search_response(curdir):
    root = os.path.abspath(curdir)
    path = os.path.join(root, 'fixtures', 'page_search_response.json')

    f = open(path, 'r')
    yield json.load(f)

    f.close()


@pytest.fixture
def config(monkeypatch, curdir):
    root = os.path.abspath(curdir)
    monkeypatch.setattr('qordoba.settings.SETTING_PATHS', (os.path.join(root, 'fixtures', '.qordoba.yml'), ))
    return load_settings()


@pytest.fixture
def mock_input(monkeypatch):
    input_mock = MagicMock()
    monkeypatch.setattr('qordoba.commands.utils.ask_simple', input_mock)
    return input_mock


@pytest.fixture
def curdir():
    return os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def projectdir(curdir):
    return os.path.abspath(os.path.join(curdir, '../'))

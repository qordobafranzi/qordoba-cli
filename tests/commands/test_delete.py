import pytest
from mock import MagicMock, patch, Mock

from qordoba.commands.delete import delete_command
from qordoba.languages import get_destination_languages
from qordoba.project import ResponsePaginatedResult, QordobaResponseError


@pytest.fixture
def mock_api(monkeypatch):
    # ProjectAPI.delete_page = Mock()
    # ProjectAPI.get_project = Mock()
    api_mock = MagicMock()
    monkeypatch.setattr('qordoba.commands.delete.ProjectAPI', api_mock)
    return api_mock.return_value


@pytest.fixture
def page_search_paginated(page_search_response):
    return ResponsePaginatedResult('pages', lambda *args, **kwargs: page_search_response, (), {})


def test_delete(mock_api, project_response, curdir):
    mock_api.get_project.return_value = project_response
    mock_api.delete_page.return_value = {'success': True}

    page_id = 1
    delete_command(curdir, {}, page_id, force=True)

    assert mock_api.get_project.call_count == 1
    mock_api.delete_page.assert_called_once_with(page_id)


def test_delete_by_filename(mock_api, project_response, curdir, page_search_paginated):
    mock_api.get_project.return_value = project_response
    mock_api.delete_page.return_value = {'success': True}
    mock_api.page_search.return_value = page_search_paginated

    lang = next(get_destination_languages(project_response))

    page_name = 'test.json'
    page_id = 1

    delete_command(curdir, {}, page_name, force=True)

    assert mock_api.get_project.call_count == 1
    assert mock_api.page_search.call_count == 1
    mock_api.page_search.assert_called_once_with(lang.id, search_string=page_name)
    mock_api.delete_page.assert_called_once_with(page_id)


def test_delete_not_found(mock_api, project_response, curdir, page_search_paginated):
    mock_api.get_project.return_value = project_response
    mock_api.delete_page.return_value = {'success': True}
    mock_api.page_search.return_value = page_search_paginated

    lang = next(get_destination_languages(project_response))

    page_name = 'test22.json'

    delete_command(curdir, {}, page_name, force=True)

    assert mock_api.get_project.call_count == 1
    assert mock_api.page_search.call_count == 1
    mock_api.page_search.assert_called_once_with(lang.id, search_string=page_name)
    assert mock_api.delete_page.call_count == 0


def test_delete_response_not_found(mock_api, project_response, curdir):
    mock_api.get_project.return_value = project_response
    mock_api.delete_page.side_effect = QordobaResponseError('Not found')

    page_id = 1
    with pytest.raises(QordobaResponseError):
        delete_command(curdir, {}, page_id, force=True)

    assert mock_api.get_project.call_count == 1
    mock_api.delete_page.assert_called_once_with(page_id)



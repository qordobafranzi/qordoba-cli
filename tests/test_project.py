import pytest

from copy import deepcopy

from qordoba.project import ResponsePaginatedResult
from tests.assertions import assert_deep_equal


@pytest.fixture
def api_pages_response(page_search_response):
    page_search_response_1 = deepcopy(page_search_response)
    page_search_response_1['meta']['paging']['total_results'] = 6
    page_search_response_2 = deepcopy(page_search_response)
    page_search_response_2['meta']['paging']['total_results'] = 6

    iterable = iter((page_search_response_1, page_search_response_2))

    return lambda *args, **kwargs: next(iterable)


def test_paginated_result(api_pages_response, page_search_response):
    query = ResponsePaginatedResult('pages', api_pages_response, (), {})
    query.request_next()

    assert len(query) == 6

    records = list(query.get(2))
    assert len(records) == 2
    assert query.has_next()

    record = query.get_one()
    assert_deep_equal(page_search_response['pages'][0], record)

    records = list(query.filter_by(lambda p: p['url'] == 'test.yml'))
    assert len(records) == 2

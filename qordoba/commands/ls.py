from __future__ import unicode_literals, print_function

from collections import namedtuple
from datetime import datetime

import logging

from qordoba.languages import get_destination_languages
from qordoba.project import ProjectAPI

log = logging.getLogger('qordoba')


class ResultRow(namedtuple('_ResultRow', ('id', 'name', 'segments', 'updated_on', 'status'))):
    pass


def ls_command(config):
    api = ProjectAPI(config)
    project = api.get_project()

    lang = next(get_destination_languages(project))

    for page in api.page_search(lang.id):
        if page.get('deleted', False):
            continue
        yield ResultRow(
            page['page_id'],
            page['url'],
            page['segment_count'],
            datetime.fromtimestamp(page['update'] / 1e3),
            'Enabled' if page.get('enabled') else ''
        )

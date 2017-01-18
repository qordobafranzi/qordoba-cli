from __future__ import unicode_literals, print_function

import logging
import os

from qordoba.languages import get_source_language, get_destination_languages, init_language_storage
from qordoba.project import ProjectAPI
from qordoba.settings import save_settings, get_push_pattern
from qordoba.sources import find_files_by_pattern, validate_path, validate_push_pattern

log = logging.getLogger('qordoba')


class FilesNotFound(Exception):
    """
    Files not found
    """


def push_command(curdir, config, files=(), version_tag=None, force=False):
    api = ProjectAPI(config)
    init_language_storage(api)

    if not files:
        pattern = get_push_pattern(config)
        pattern = validate_push_pattern(pattern)
        files = list(find_files_by_pattern(curdir, pattern))
        if not files:
            raise FilesNotFound('Files not found by pattern `{}`'.format(pattern))

    project = api.get_project()
    source_lang = get_source_language(project)

    for file in files:
        path = validate_path(curdir, file, source_lang)
        log.info('Uploading {}'.format(path.native_path))

        file_name = path.unique_name

        with open(path.native_path, 'rb') as f:
            resp = api.upload_file(f, file_name, mimetype='application/octet-stream', force=force)

        log.info('Uploaded {} successfully'.format(path.native_path))

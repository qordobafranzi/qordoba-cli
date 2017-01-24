from __future__ import unicode_literals, print_function

import logging
import os

from qordoba.commands.utils import ask_question
from qordoba.languages import get_source_language, init_language_storage
from qordoba.project import ProjectAPI
from qordoba.settings import get_push_pattern
from qordoba.sources import find_files_by_pattern, validate_path, validate_push_pattern, get_content_type_code

log = logging.getLogger('qordoba')


class FilesNotFound(Exception):
    """
    Files not found
    """


def select_version_tag(file_name, version_tags):
    log.info('File `{}` already exist with tags {}. Please setup new version tag:'
             .format(file_name, ', '.join(version_tags)))

    version_tag = None
    while version_tag is None:
        user_tag = ask_question('VersionTag: ')
        if user_tag not in version_tags:
            version_tag = user_tag

    return version_tag


def upload_file(api, project, path, **kwargs):
    log.info('Uploading {}'.format(path.native_path))

    file_name = path.unique_name
    content_type_code = get_content_type_code(path)
    version_tag = None

    with open(path.native_path, 'rb') as f:
        resp = api.upload_anytype_file(f, file_name, content_type_code, **kwargs)
    log.debug('File `{}` uploaded. Name - `{}`. Adding to the project...'.format(path.native_path, file_name))

    if resp.get('version_tags', ()):
        version_tag = select_version_tag(file_name, resp.get('version_tags'))

    resp = api.append_file(resp['upload_id'], file_name, version_tag=version_tag, **kwargs)

    log.info('Uploaded {} successfully'.format(path.native_path))


def push_command(curdir, config, files=()):
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

        upload_file(api, project, path)

from __future__ import unicode_literals, print_function

import logging
import os

from qordoba.commands.utils import ask_question
from qordoba.languages import get_source_language, init_language_storage, get_destination_languages
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


def upload_file(api, path, version=None, **kwargs):
    log.info('Uploading {}'.format(path.native_path))

    file_name = path.unique_name
    content_type_code = get_content_type_code(path)
    version_tag = version

    with open(path.native_path, 'rb') as f:
        resp = api.upload_anytype_file(f, file_name, content_type_code, **kwargs)
    log.debug('File `{}` uploaded. Name - `{}`. Adding to the project...'.format(path.native_path, file_name))

    if resp.get('version_tags', ()):
        if version_tag is None or version_tag in resp.get('version_tags'):
            version_tag = select_version_tag(file_name, resp.get('version_tags'))

    resp = api.append_file(resp['upload_id'], file_name, version_tag=version_tag, **kwargs)

    log.info('Uploaded {} successfully as {}'.format(path.native_path, file_name))


def update_file(api, path, remote_files, version=None):
    file_name = path.unique_name

    log.info('Updating {}'.format(path.unique_name))
    if version:
        remote_file = next((f for f in remote_files if f.get('version_tag', None) == version), None)
        if not remote_file:
            raise FilesNotFound('File {} with version {} not found'.format(file_name, version))
    else:
        remote_file = remote_files[0]

    with open(path.native_path, 'rb') as f:
        resp = api.update_upload_anyType_file(f, file_name, remote_file['page_id'])

    resp = api.apply_upload_file(resp['id'], remote_file['page_id'])

    log.info('Updated {} successfully.'.format(file_name))


def push_command(curdir, config, update=False, version=None, files=()):
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
    lang = next(get_destination_languages(project))

    for file in files:
        path = validate_path(curdir, file, source_lang)

        file_name = path.unique_name

        remote_file_pages = list(api.page_search(language_id=lang.id, search_string=file_name))

        if remote_file_pages and update:
            update_file(api, path, remote_file_pages, version=version)
        else:
            upload_file(api, path, version=version)

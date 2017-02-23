import pytest

from qordoba.languages import Language
from qordoba.sources import validate_push_pattern, PatternNotValid, create_target_path_by_pattern, to_native

PATTERN1 = 'i18n/<language_code>/translations.json'
PATTERN2 = 'folder1/values-<language_lang_code>/strings.xml'
PATTERN3 = 'config/locales/server.<language_code>.yml'

PATTERN4 = 'folder2/<language_name>/strings.xml'
PATTERN5 = 'folder3/strings.<language_name_cap>'
PATTERN6 = '<language_name_allcap>.locale'

PATTERN_PUSH1 = 'config/*'
PATTERN_PUSH2 = './*/*.json'
PATTERN_PUSH3 = 'sources/[0-9]/*'
PATTERN_PUSH4 = 'folder1/values-*/strings.xml'


PATTERN_PUSH_INVALID1 = 'i18n/<language_lang>/translations.json'
PATTERN_PUSH_INVALID2 = ''
PATTERN_PUSH_INVALID3 = './sources/'

PATH1 = 'i18n/fr-fr/translations.json'

paths = (
    'i18n/fr-fr/translations.json',
    'i18n/en/translations.json',
    'i18n/en_US/translations.json'
)

LANGUAGE_EN = Language({
            "id": 94,
            "name": "English - United States",
            "code": "en-us",
            "direction": "ltr",
            "override_order": "aaa - aaa - English - United States"
})

LANGUAGE_FR = Language({
    "id" : 110,
    "name" : "French - France",
    "code" : "fr-fr",
    "direction" : "ltr",
    "override_order" : "aaa - naa - French - France"
  })

LANGUAGE_CN = Language({
    "id" : 46,
    "name" : "Chinese - China",
    "code" : "zh-cn",
    "direction" : "ltr",
    "override_order" : "Chinese - China"
})


@pytest.mark.parametrize('pattern', [PATTERN_PUSH1, PATTERN_PUSH2, PATTERN_PUSH3])
def test_validate_push_pattern(pattern):
    res = validate_push_pattern(pattern)


@pytest.mark.parametrize('invalid_pattern', [PATTERN_PUSH_INVALID1,
                                             PATTERN_PUSH_INVALID2,
                                             PATTERN_PUSH_INVALID3,
                                             ])
def test_validate_push_pattern_invalid(invalid_pattern):
    with pytest.raises(PatternNotValid):
        validate_push_pattern(invalid_pattern)


@pytest.mark.parametrize('invalid_pattern', [PATTERN_PUSH_INVALID1,
                                             PATTERN_PUSH_INVALID2,
                                             PATTERN_PUSH_INVALID3
                                             ])
def test_create_target_path_by_pattern_invalid(invalid_pattern, projectdir):
    with pytest.raises(PatternNotValid):
        create_target_path_by_pattern(projectdir, None, None, pattern=invalid_pattern)


@pytest.mark.parametrize('pattern,target_language,expected', [
    (PATTERN1, LANGUAGE_CN, to_native('i18n/zh-cn/translations.json')),
    (PATTERN2, LANGUAGE_EN, to_native('folder1/values-en/strings.xml')),
    (PATTERN3, LANGUAGE_FR, to_native('config/locales/server.fr-fr.yml')),
    (PATTERN4, LANGUAGE_CN, to_native('folder2/Chinese/strings.xml')),
    (PATTERN5, LANGUAGE_FR, to_native('folder3/strings.French')),
    (PATTERN6, LANGUAGE_FR, 'FRENCH.locale')
])
def test_create_target_path_by_pattern(mock_lang_storage, pattern, target_language, expected):
    res = create_target_path_by_pattern('', target_language, None, pattern=pattern)
    assert res.native_path == expected

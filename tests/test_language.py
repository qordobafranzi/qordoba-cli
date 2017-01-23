import pytest

from qordoba.languages import get_source_language, Language, get_destination_languages, normalize_language, \
    LanguageNotFound


@pytest.fixture
def lang_en_us(lang_en_data):
    return Language(lang_en_data)


@pytest.fixture()
def lang_en_gb():
    return Language({
        "id": 92,
        "name": "English - United Kingdom",
        "code": "en-gb",
        "direction": "ltr"
    })


def test_get_source_language(project_response, lang_en_us):
    lang = get_source_language(project_response)

    assert lang == lang_en_us


def test_get_destination_language(project_response, lang_en_gb):
    langs = list(get_destination_languages(project_response))
    assert len(langs) == 3
    assert lang_en_gb in langs


def test_language_object(lang_en_us, lang_en_gb, lang_en_data):
    assert lang_en_us.code == 'en-us'
    assert lang_en_us.id == 94
    assert lang_en_us.lang == 'en'
    assert lang_en_us.name == 'English'

    assert lang_en_us == Language(lang_en_data)

    assert lang_en_us.lang == lang_en_gb.lang
    assert lang_en_us != lang_en_gb
    assert lang_en_us.name == lang_en_gb.name


def test_normalize_language(mock_lang_storage, lang_en_us, lang_en_gb):
    res = normalize_language('en_US')

    assert res == lang_en_us
    assert res.code == 'en-us'

    res = normalize_language('EN-GB')

    assert res == lang_en_gb
    assert res.code == 'en-gb'

    res = normalize_language('en')

    assert res == lang_en_us
    assert res.code == lang_en_us.code


def test_normalize_language_error(mock_lang_storage):
    with pytest.raises(LanguageNotFound):
        normalize_language('ed-ed')

    with pytest.raises(LanguageNotFound):
        normalize_language('')




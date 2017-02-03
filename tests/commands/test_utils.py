import pytest

from tests.assertions import assert_deep_equal
from qordoba.commands.utils import ask_question, ask_bool, ask_select, ask_select_multiple


@pytest.mark.parametrize('question,answer,answer_type', [
    ('question1', 22, int),
    ('question2', 'answer', str)
])
def test_ask_question(mock_input, question, answer, answer_type):
    mock_input.side_effect = (answer, )
    res = ask_question(question, answer_type)

    mock_input.assert_called_once_with(question)
    assert res == answer


@pytest.mark.parametrize('question,answers,answer_type', [
    ('question1', ('error', 22), int),
    ('question2', (object, 'answer'), lambda x: x[:])
])
def test_ask_question_error(mock_input, question, answers, answer_type):
    mock_input.side_effect = answers
    res = ask_question(question, answer_type, exceptions=(TypeError, ValueError))

    assert mock_input.call_count == 2
    assert res == answers[-1]


@pytest.mark.parametrize('question,answers,expected', [
    ('question1', ('error', 'y'), True),
    ('question2', (-1, 'N'), False),
    ('question3', (object, 'Yes'), True),
    ('question4', ('noo', 'No'), False),
    ('question5', (1, 'Y'), True),
])
def test_ask_bool(mock_input, question, answers, expected):
    mock_input.side_effect = answers

    res = ask_bool(question)

    assert res == expected
    assert mock_input.call_count == 2
    mock_input.assert_called_with('[Y/n]')


@pytest.mark.parametrize('question_list,answers,promt,expected', [
    (('question1', 'question2'), ('error', 1), 'Select: ','question1'),
    (('question3', 'question4'), (object, 2), 'Set: ', 'question4'),
])
def test_ask_select(mock_input, question_list, answers, promt, expected):
    mock_input.side_effect = answers

    res = ask_select(question_list, promt)

    assert res == expected
    assert mock_input.call_count == 2
    mock_input.assert_called_with(promt)


@pytest.mark.parametrize('question_list,answers,promt,expected', [
    ((('1', 'question1'), ('25', 'question2')), ('3,5', '1,2'), 'Select: ', (('1', 'question1'), ('25', 'question2'))),
    ((('ID-1', 'question3'), ('1', 'question4'), ('NONID', 'question5')), ('error', '1 2'), 'Set: ', (('ID-1', 'question3'), ('1', 'question4'))),
])
def test_ask_select_multiple(mock_input, question_list, answers, promt, expected):
    mock_input.side_effect = answers

    res = ask_select_multiple(question_list, promt)

    assert_deep_equal(res, expected)
    assert mock_input.call_count == 2
    mock_input.assert_called_with(promt)


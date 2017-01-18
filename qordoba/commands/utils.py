from __future__ import unicode_literals, print_function

import sys
import errno
import logging
import os

log = logging.getLogger('qordoba')

PY3 = sys.version_info[0] == 3
if PY3:
    cli_input = input
else:
    cli_input = raw_input



def prompt_select(question_list, prompt='Select:'):
    """

    :param question_list: Excpect list of tuples with 2 elements - ID and TEXT
    :param prompt: First message.
    :return: ID or TEXT
    """

    valid_answers = list((el + 1 for el in range(len(question_list))))

    question_list_text = []
    for el_num, question in enumerate(question_list, start=1):
        try:
            _, text = question
        except ValueError:
            text = question

        question_list_text.append('{}) {}'.format(el_num, text))

    promt_message = '\n'.join(question_list_text + [prompt, ])
    answer = None
    while answer not in valid_answers:
        try:
            answer = int(cli_input(promt_message))
        except (TypeError, ValueError):
            promt_message = prompt

    return question_list[answer - 1]


def prompt(question='[Y/n]?'):
    """
    Ask user a question in intercative mode
    """
    yes = ['Y', 'y', 'Yes', 'yes', ]
    no = ['N', 'n', 'No', 'no', ]
    valid = yes + no

    answer = None
    while answer not in valid:
        answer = cli_input(question)
        question = '[Y/n]'

    return answer in yes


def mkdirs(path):
    try:
        if path:
            os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise

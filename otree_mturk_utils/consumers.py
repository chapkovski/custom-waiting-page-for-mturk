from channels import Group
from .models import Mturk, WPJobRecord, WPTimeRecord, ROWS, BigFiveData
from random import randint
from otree.models import Participant
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from importlib import import_module
import json


def get_models_module(app_name):
    module_name = '{}.models'.format(app_name)
    return import_module(module_name)


# ============= For creating a task
def slicelist(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def get_random_list():
    max_len = 100
    low_upper_bound = 50
    high_upper_bound = 99
    return [randint(10, randint(low_upper_bound, high_upper_bound)) for i in range(max_len)]


def get_task():
    string_len = 10
    listx = get_random_list()
    listy = get_random_list()
    answer = max(listx) + max(listy)
    listx = slicelist(listx, string_len)
    listy = slicelist(listy, string_len)
    return {
        "message_type": "new_task",
        "mat1": listx,
        "mat2": listy,
        "correct_answer": answer,
    }


def send_message(message, app_name, group_pk, gbat, index_in_pages):
    those_with_us = get_models_module(app_name).Player.objects.filter(
        group__pk=group_pk,
        participant__mturk__current_wp=index_in_pages,
    )
    how_many_arrived = len(those_with_us)
    print('HOW MANY ARRIVED:', how_many_arrived)
    players_per_group = get_models_module(app_name).Constants.players_per_group
 
    left_to_wait = players_per_group - how_many_arrived

    textforgroup = json.dumps({
        "message_type": "players_update",
        "how_many_arrived": how_many_arrived,
        "left_to_wait": left_to_wait,
    })
    Group('group_{}'.format(group_pk)).send({
        "text": textforgroup,
    })


def ws_connect(message, participant_code, app_name, group_pk, player_pk, index_in_pages, gbat):
    print('somebody connected from custom wp..')
    try:
        mturker = Mturk.objects.get(Participant__code=participant_code)
    except ObjectDoesNotExist:
        return None

    mturker.current_wp = index_in_pages
    mturker.save()
    new_task = get_task()
    wprecord, created = mturker.wpjobrecord_set.get_or_create(app=app_name, page_index=index_in_pages)
    wprecord.last_correct_answer = new_task['correct_answer']
    wprecord.save()
    new_task['tasks_correct'] = wprecord.tasks_correct
    new_task['tasks_attempted'] = wprecord.tasks_attempted
    message.reply_channel.send({'text': json.dumps(new_task)})

    Group('group_{}'.format(group_pk)).add(message.reply_channel)
    send_message(message, app_name, group_pk, gbat, index_in_pages)


def ws_message(message, participant_code, app_name, group_pk, player_pk, index_in_pages, gbat):
    jsonmessage = json.loads(message.content['text'])
    answer = jsonmessage.get('answer')

    if answer:
        with transaction.atomic():
            try:
                mturker = Mturk.objects.select_for_update().get(Participant__code=participant_code)
                wprecord = WPJobRecord.objects.get(mturker=mturker,
                                                   page_index=index_in_pages,
                                                   app=app_name)
            except ObjectDoesNotExist:
                return None

            wprecord.tasks_attempted += 1

            if int(answer) == int(wprecord.last_correct_answer):
                wprecord.tasks_correct += 1

            new_task = get_task()
            new_task['tasks_correct'] = wprecord.tasks_correct
            new_task['tasks_attempted'] = wprecord.tasks_attempted
            wprecord.last_correct_answer = new_task['correct_answer']
            wprecord.save()

        message.reply_channel.send({'text': json.dumps(new_task)})


# Connected to websocket.disconnect
def ws_disconnect(message, participant_code, app_name, group_pk, player_pk, index_in_pages, gbat):
    try:
        mturker = Mturk.objects.get(Participant__code=participant_code)
    except ObjectDoesNotExist:
        return None

    mturker.current_wp = None
    mturker.save()
    print('somebody disconnected...')
    Group('group_{}'.format(group_pk)).discard(message.reply_channel)
    send_message(message, app_name, group_pk, gbat, index_in_pages)







def big_connect(message, participant_code):
    print('connected')


def big_message(message, participant_code):
    jsonmessage = json.loads(message.content['text'])
    print("json:::", jsonmessage)

    dictionary = jsonmessage['answers']
    answer_vector = []
    num_questions=len(ROWS)
    for i in range(0, num_questions):
        try:
            answer_vector.append(dictionary[str(i)])
        except KeyError:
            answer_vector.append("0")

    data, created = BigFiveData.objects.get_or_create(Participant__code=participant_code)
    data.bigfive = answer_vector
    data.save()
    print("bigfive::::", data.bigfive)


def big_disconnect(message, participant_code):
    print('disconnected')
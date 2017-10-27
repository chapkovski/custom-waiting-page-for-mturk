from channels import Group
from channels.sessions import channel_session
import random
from .models import Player, Subsession, Constants, Group as OtreeGroup
import json
import random
from random import randint

# =============
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


def send_message(message, group_pk, gbat, index_in_pages):
    those_with_us = Player.objects.filter(
        group__pk=group_pk,
        current_wp=index_in_pages,
    )
    how_many_arrived = len(those_with_us)
    left_to_wait = Constants.players_per_group - how_many_arrived
    textforgroup = json.dumps({
        "message_type": "players_update",
        "how_many_arrived": how_many_arrived,
        "left_to_wait": left_to_wait,
    })
    Group('group_{}'.format(group_pk)).send({
        "text": textforgroup,
    })


def ws_connect(message, participant_code, group_pk, player_pk, index_in_pages, gbat):
    print('somebody connected...')
    player = Player.objects.get(pk=player_pk, participant__code_exact=participant_code )
    player.current_wp = index_in_pages
    new_task = get_task()
    player.last_correct_answer = new_task['correct_answer']
    player.save()
    message.reply_channel.send({'text': json.dumps(new_task)})

    Group('group_{}'.format(group_pk)).add(message.reply_channel)
    send_message(message, group_pk, gbat, index_in_pages)







def ws_message(message, participant_code, group_pk, player_pk, index_in_pages, gbat):
    jsonmessage = json.loads(message.content['text'])
    answer = jsonmessage.get('answer')
    if answer:

        player = Player.objects.get(pk=player_pk, participant__code_exact=participant_code)


        # tasks_attempted = player.participant.vars.get("tasks_attempted" , 0) + 1
        # player.participant.vars.set("tasks_attempted" , tasks_attempted)
        add_one(player, "tasks_attempted")

        player.tasks_attempted += 1
        if int(answer) == int(player.last_correct_answer):
            player.tasks_correct += 1
            # tasks_correct = player.participant.vars.get("tasks_correct" , 0) + 1
            # player.participant.vars.set("tasks_correct" , tasks_correct)
            add_one(player, "tasks_correct")

        new_task = get_task()
        new_task['tasks_correct'] = player.tasks_correct
        new_task['tasks_attempted'] = player.tasks_attempted
        player.last_correct_answer = new_task['correct_answer']
        player.save()
        message.reply_channel.send({'text': json.dumps(new_task)})



# Connected to websocket.disconnect
def ws_disconnect(message, participant_code, group_pk, player_pk, index_in_pages, gbat):
    player = Player.objects.get(pk=player_pk)
    player.current_wp = None
    player.save()
    print('somebody disconnected...')
    Group('group_{}'.format(group_pk)).discard(message.reply_channel)
    send_message(message, group_pk, gbat, index_in_pages)


def add_one(player, name_of_the_record):
    var = player.participant.vars.get(name_of_the_record, 0) + 1
    player.participant.vars[name_of_the_record] = var



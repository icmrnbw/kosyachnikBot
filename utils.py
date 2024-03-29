from datetime import datetime, timedelta, timezone
from random import choice
from typing import Tuple

import pytz
from telegram import Update

from messages import WAIT_MSG, PARTICIPANTS_LIST
from storage import storage
from pytz import all_timezones


# offset = timedelta(hours=-4)
# timezone(offset, name='EST')


def verbose_format_time(h, m, s) -> str:
    """ Accepts a number of hours, minutes and seconds. Returns a string with correct plural and singular forms of words. """

    def determine_suffix(val: int, words: Tuple[str, str, str]):
        if 1 < val % 10 < 5 and (val < 10 or val > 20):
            return str(val) + words[0]
        elif val % 10 == 1 and (val > 11 or val < 10):
            return str(val) + words[1]
        elif val == 0:
            return ''
        else:
            return str(val) + words[2]

    time_dict = {'hours': determine_suffix(h, (' hours, ', ' hour, ', ' hours, ')), 'minutes': determine_suffix(m, (' minutes, ', ' minute, ', ' minutes, ')),
                 'seconds': determine_suffix(s, (' seconds', ' second', ' seconds'))}
    time = ''

    for keys in time_dict:
        time = time + time_dict[keys]

    return time




async def check_time(update: Update) -> Tuple[bool, datetime]:
    """ Returns time(timedelta) passed since the last function call and a formatted message with this timedelta. THIS IS AN OLD COMMENT, GOTTA UPDATE"""
    chat_id = update.message.chat.id
    time_zone = pytz.timezone('Asia/Samarkand')
    # Fetching datetime.now making it first timezone-aware and then timezone-naive making it still show the timezone we need
    now = datetime.now(time_zone).replace(tzinfo=None)
    # Selecting a timezone-naive timestamp with the timezone we need (in this case, GMT +5)
    time = await storage.retrieve_time(chat_id=chat_id)
    print(now, time)
    last_time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S') #.replace(tzinfo=time_zone)
    check_day_passed = now.year > last_time.year or now.month > last_time.month or now.day > last_time.day
    return check_day_passed, now


def get_wait_text(now, winner_name):
    minutes, seconds, hours = (60 - now.minute, 60 - now.second, 23 - now.hour)
    if hours != 0:
        seconds = 0
        time_string = verbose_format_time(hours, minutes, seconds)
        time_string = time_string.rstrip(', ')
    else:
        time_string = verbose_format_time(hours, minutes, seconds)
    wait_text = WAIT_MSG.format(time=time_string, winner_name=winner_name)
    return wait_text


async def format_participants_list(chat_id) -> str:
    """ Formats a list of registered members of the effective chat to display it as a message later. """
    participants_list = await storage.retrieve_participants_list(chat_id=chat_id)

    participants_list_to_format = []

    for i in participants_list:
        participants_list_to_format.append(f'<i>{i["username"] or i["name"]}</i>')

    participants_list_message = ', '.join(participants_list_to_format)
    participants_text = PARTICIPANTS_LIST.format(list_of_participants=participants_list_message)

    return participants_text


async def choose_random_winner(chat_id) -> Tuple[int, str]:
    """ Randomly chooses a Kosyachnik among registered members of the effective chat and increments his score. """
    participants_list = await storage.retrieve_participants_list(chat_id=chat_id)

    winner = choice(participants_list)
    winner_id = winner['id']
    winner_name = winner['username'] or winner['name']
    winner_name = '@' + winner_name if winner['username'] else winner_name
    await storage.increment_row(chat_id, winner_id)

    return winner_id, winner_name

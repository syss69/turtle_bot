import logging
import sys
import threading
import time
import asyncio

import requests

sys.path.append('lib/')

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard
from vk_api.utils import get_random_id
import setting

def get_chat_owner(peer_id: int) -> list:
    info = vk.messages.getConversationsById(peer_ids=peer_id)
    owner = info['items'][0]['chat_settings']['admin_ids']
    owner.append(info['items'][0]['chat_settings']['owner_id'])
    return owner


def family_send(peer: int, fam: list, prefix: str, msg: str) -> None:
    prefix = str(prefix)
    keyboard = VkKeyboard(inline=True)
    keyboard.add_button(prefix + fam[0], color='default')
    del fam[0]
    for i in fam:
        keyboard.add_line()
        keyboard.add_button(prefix + i, color='default')
    vk.messages.send(peer_id=peer, random_id=get_random_id(), keyboard=keyboard.get_keyboard(),
                     message=msg)


def send_message(peer: int, message: str) -> None:
    asyncio.run(async_send_message(peer, message))


async def async_send_message(peer: int, message: str):
    try:
        vk.messages.send(
            random_id=get_random_id(),
            peer_id=peer,
            message=message)
    except vk_api.exceptions.ApiError:
        await asyncio.sleep(1)
        send_message(peer, message)


arrayGroup = ['TESTGROUP', 'DEVGROUP']
arrayPrepods = []

vk_session = vk_api.VkApi(token=setting.BOT_TOKEN)
vk = vk_session.get_api()
command_list = []

while True:
    vk_session = vk_api.VkApi(
        token=setting.BOT_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, '164805438')
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            text = event.raw['object']['message']['text']  # текст сообщения
            user_id = event.raw['object']['message']['from_id']  # id пользователя который отправил сообщение
            id = event.raw['object']['message'][
                'id']  # id беседы (для лс будет равен нулю) НЕ! НАОБОРОТ! В ЛС ОН НЕ РАВЕН 0
            peer = event.raw['object']['message'][
                'peer_id']  # откуда отправлено сообщение (как правило туда и возвращается ответ)
            if text.lower() == 'chatid':
                send_message(peer, peer)




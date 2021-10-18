import logging
import queue
import threading
import time
from typing import List
from typing import Union

import requests
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

import database
import urlprepod
from classes import Prepods
import setting

VK_API = vk_api.VkApi(token=setting.BOT_TOKEN)
VK_API = VK_API.get_api()

with database.DbSchedule() as db:
    GROUP = db.take_group()

message_queue = queue.Queue()

logging.basicConfig(filename='command.log',
                    filemode='a',
                    format='%(asctime)s %(levelname)s %(filename)s - %(funcName)s: %(message)s',
                    level=logging.INFO)


def retake_list_prepods_and_group() -> None:
    time.sleep(3600 * 24)
    with database.DbSchedule() as db:
        GROUP = db.take_group()
        GROUP.append('TESTGROUP')

threading.Thread(target=retake_list_prepods_and_group).start()
GROUP.append('TESTGROUP')


class Command:
    def __init__(self, user_id: int, peer: int, chat_id: int, text: str):
        command_dict = {'start': {"synonym": ['помощь', 'начать', 'help'], 'func': self.start_msg},
                        'apair_all': {"synonym": ['пары на неделю ', "расписание на неделю "],
                                      'func': self.apair_all_day},
                        'apair_two_day': {"synonym": ['пары ', "расписание ", "занятия ", "занятие "],
                                          'func': self.apair_two_day},
                        'my_group': {"synonym": ['моя группа '], 'func': self.my_group},
                        'family': {"synonym": ['фио ', "фамилия ", "препод "], 'func': self.fio},
                        'sub_group': {
                            "synonym": ["уведомления для ", "уведомление для ", "уведомление ", 'уведомления '],
                            'func': self.sub_group},
                        'del_sub': {"synonym": ["отписаться"], 'func': self.del_sub},
                        'queue_size': {"synonym": ["длина очереди"], 'func': self.send_queue},
                        'del_keyboard': {"synonym": ["убери клавиатуру"], 'func': self.del_keyboard},
                        'url_sender': {"synonym": ["ссылка на "], 'func': self.url_prepod_send},
                        'new_prepod': {"synonym": ["новый препод "], 'func': self.new_prepod},
                        'group_sender': {"synonym": ["рассылка "], 'func': self.group_sender},
                        'group_suber': {"synonym": ["подписчики "], 'func': self.take_group_details},
                        'user_group': {"synonym": ["группа "], 'func': self.take_user_group}
                        }

        self.peer = peer
        self.user_id = user_id
        self.chat_id = chat_id
        self.text = text.lower()
        self.args = []
        self.command = ''
        break_block = False
        for command in command_dict:
            for synonym_command in command_dict[command]['synonym']:
                synonym_command_len = len(synonym_command)
                if synonym_command == self.text[:synonym_command_len]:
                    cmd = self.text[:synonym_command_len]
                    self.args = self.text.split(cmd)
                    self.command = cmd
                    del self.args[0]
                    command_dict[command]['func']()
                    break_block = True
                    break
            if break_block:
                break

    def my_stick(self):
        gifts = VK_API.gifts.get(user_id=self.user_id,count=20000)
        stickers = list(filter(lambda x: x['gift'].get('stickers_product_id'), gifts['response']['items']))
        print(stickers)

    def start_msg(self):
        command_text = '\n📜 пары [группа/преподователь] - выводит какие пары сегодня у [группы/преподователь].' \
                       '\nПример: пары пи-41' \
                       '\n📜 пары на неделю [группа] - выводит какие пары у [группы] за неделю.' \
                       '\nПример: пары на неделю пи-41' \
                       '\n\n👤 фио [Фамилия препода] - поиск по фамиили преподавателей.' \
                       '\nПример: фио Шашкин' \
                       '\n\n📌 моя группа [группа] - отправляет клавиатуру с командами для [группа].' \
                       '\nПример: моя группа пи-41' \
                       '\n🚫 убери клавиатуру - убирает клавиатуру вызванную командой "моя группа"' \
                       '\n\n🔔 уведомления для [группа] - отправляет уведомления для [группа].' \
                       '\nПример: уведомления для пи-41' \
                       '\n🔕 отписаться - отписаться от всех уведомлений.' \
                       '\n\n🔎 ссылка на [фамилия] - берет ссылку на онлайн кабинет преподователя [фамилия].' \
                       '\n\nПредложения рассматриваются в ЛС @al_shashkin. Рекламу не продаю.'
        return self.send_message(command_text)

    def apair_two_day(self):
        """
       Отправляет расписание для группы cmd
       :param peer: кому отправить
       :param cmd: группа для запроса расписания с базы
       :param amount: количество дней необходимых на возврат (none - все дни)
       :param conv_id: айди беседы, 0 если личка
       :param user_id: айди пользователя
       """
        NUMBER_SMILE_CODE = '&#8419;'
        cmd = self.args[0].upper()
        with database.DbSchedule() as db:
            result_query = db.select_shcedule(cmd)
        apair_list = result_query['schedule']
        amount = 0
        if apair_list:
            message = result_query['name'] + '\n\n'
            for day in apair_list:
                message += '\n\n--------------------\n'
                message += "&#128197; " + day
                message += '\n--------------------\n'
                for hour in apair_list[day]:
                    message += '\n&#9203; {} {}\n'.format(hour,
                                                          str(apair_list[day][hour][0]['number']) + NUMBER_SMILE_CODE)
                    for parainfo in apair_list[day][hour]:
                        message += "📖 {}\n&#127891; {}\n&#128273; {}\n🏢 {}\n".format(parainfo['doctrine'],
                                                                                       parainfo['teacher'],
                                                                                       parainfo['auditoria'],
                                                                                       parainfo['corpus'])
                        if len(apair_list[day][hour]) > 1:
                            message += '\n'
                amount += 1
                if amount == 2:
                    break
        else:
            message = '[⛔] Пар нет/группа указана неправильно.'
        return self.send_message(message)

    def apair_all_day(self):
        NUMBER_SMILE_CODE = '&#8419;'
        cmd = self.args[0].upper()
        with database.DbSchedule() as db:
            result_query = db.select_shcedule(cmd)
        apair_list = result_query['schedule']
        if apair_list:
            message = result_query['name'] + '\n\n'
            for day in apair_list:
                message += '\n\n--------------------\n'
                message += "&#128197; " + day
                message += '\n--------------------\n'
                for hour in apair_list[day]:
                    message += '\n&#9203; {} {}\n'.format(hour,
                                                          str(apair_list[day][hour][0]['number']) + NUMBER_SMILE_CODE)
                    for parainfo in apair_list[day][hour]:
                        message += "📖 {}\n&#127891; {}\n&#128273; {}\n🏢 {}\n".format(parainfo['doctrine'],
                                                                                       parainfo['teacher'],
                                                                                       parainfo['auditoria'],
                                                                                       parainfo['corpus'])
                        if len(apair_list[day][hour]) > 1:
                            message += '\n'
        else:
            message = '[⛔] Пар нет/группа указана неправильно.'
        return self.send_message(message)

    def my_group(self):
        cmd = self.args[0]
        if cmd.upper() in GROUP:
            keyboard = Tools.take_keyboardgroup(cmd)
            if self.chat_id == 0:
                if self.user_id in Tools.get_chat_owner():
                    VK_API.messages.send(peer_id=self.peer, random_id=get_random_id(), keyboard=keyboard.get_keyboard(),
                                         message='[х]✅] Отправил тебе клавиатуру.')
            else:
                VK_API.messages.send(peer_id=self.peer, random_id=get_random_id(), keyboard=keyboard.get_keyboard(),
                                     message='[✅] Отправил тебе клавиатуру.')
        else:
            self.send_message('[⛔] Такой группы нет.')

    def del_keyboard(self):
        if self.chat_id == 0:
            if self.user_id in Tools.get_chat_owner():
                VK_API.messages.send(peer_id=self.peer, random_id=get_random_id(),
                                     keyboard=VkKeyboard().get_empty_keyboard(),
                                     message='🚫 Удаляю клавиатуру.')
        else:
            VK_API.messages.send(peer_id=self.peer, random_id=get_random_id(),
                                 keyboard=VkKeyboard().get_empty_keyboard(),
                                 message='🚫 Удаляю клавиатуру.')

    def fio(self):
        text = self.args[0]
        msg = ''
        getFamily = Prepods.find_people(text)
        if len(getFamily) == 1:
            msg = getFamily[0].full_name
        else:
            if len(getFamily) > 1:
                if getFamily[0].family != getFamily[1].family:
                    msg = 'У меня нет информации о данной фамилии.\n\n'
                    msg += '❓ Возможно, Вы искали:\n'
                    getFamily = list(map(lambda x: x.family, getFamily))
                    msg += '\n'.join(getFamily)
                    return self.family_send(getFamily, msg)
                elif getFamily[0].family == getFamily[1].family:
                    getFamily = list(map(lambda x: x.full_name, getFamily))
                    msg = '\n'.join(getFamily)
            else:
                msg = '[⛔] У меня нет информации о данной фамилии.'
        return self.send_message(msg)

    def send_queue(self):
        self.send_message(str(message_queue.qsize()))

    def bot_drop(self):
        msg = '❗ Репорт на падение от @id{} ❗\n'.format(self.user_id)
        try:
            msg += 'Код от rksi.ru: {}'.format(requests.get('https://rksi.ru/schedule').status_code)
        except Exception as e:
            msg += '\nСервер rksi.ru не отвечает: {}'.format(e.__class__.__name__)

        try:
            server_req = requests.get('https://vk.com/im')
            msg += '\nКод от сервера ВК: {}'.format(server_req.status_code)
            msg += '\nВремя задержки ответа ВК (me->vk): {}'.format(server_req.elapsed.total_seconds())
        except Exception as e:
            msg += '\nСервер vk.com не отвечает: {}'.format(e.__class__.__name__)

        with open('app.log', 'r') as f:
            all_line_error = f.readlines()
            if all_line_error[-1:] == '':
                last_error = all_line_error[-2:]
            else:
                last_error = all_line_error[-1:]
        msg += '\nПоследняя ошибка: \n{}'.format(last_error[0])

        self.send_message(msg)

    def url_prepod_send(self):
        finded = self.args[0].upper()
        result = ''
        if len(finded) > 3:
            for i in urlprepod.GoogleTables(
                    '1TYqoU3pGHd_u1UWjHV5TaHKOZr_d3nYG1MG0cVKye3Q').take_values_table():
                if i:
                    if finded in i[0].upper():
                        result += ' | '.join(i) + '\n'

        if result != '':
            return self.send_message(result)

    def new_prepod(self):
        if self.user_id == 178431948:
            cmd = ' '.join(self.args)
            cmd = cmd.split(' ')
            new = Prepods.add_perpods(cmd[0], cmd[1], cmd[2])
            self.send_message(str(new))

    def sub_group(self):
        cmd = self.args[0].upper()
        if cmd in GROUP:
            if self.chat_id == 0:
                admin_group = Tools.get_chat_owner(self.peer)
            dublicate = database.Db().check_duplicate(cmd, self.peer)
            if (not dublicate and self.chat_id == 0 and self.user_id in admin_group) \
                    or (not dublicate and self.chat_id != 0):
                database.Db().add_subscribe(cmd, self.peer)
                self.send_message(
                    f"🔔 Вы теперь подписаны на уведомления для {cmd}.\nЧтобы перестать получать уведомления напишите 'отписаться'.")
            elif self.chat_id == 0 and self.user_id not in admin_group:
                self.send_message(f'🚫 @id{self.user_id} не является администратором чата.')
            else:
                self.send_message('🚫 Повторно подписаться на одну группу нельзя.')
        else:
            self.send_message('[⛔] Вероятно, такой группы нет.')

    def del_sub(self):
        if self.chat_id != 0:
            database.Db().del_subscribe(self.peer)
            self.send_message(f"🔕 Вы отписаны от уведомлений.")
        else:
            if self.user_id in Tools.get_chat_owner(self.peer):
                database.Db().del_subscribe(self.peer)
                self.send_message(f"🔕 Вы отписаны от уведомлений.")
            else:
                self.send_message(f"[⛔] @id{self.user_id} не является администратором чата.")

    def group_sender(self):
        if Tools.is_turtle_privilege(self.user_id):
            args = self.args[0].split(' ', 1)
            args[0] = args[0].upper()
            if args[0] in GROUP:
                logging.info(
                    '{} инициализирована рассылка по группе {} с сообщением {}'.format(self.user_id, args[0], args[1]))
                groud_sub_id = database.Db().select_group(args[0])
                custom_api_object = customVkApi(VK_API)
                message = '📩 {} -> {}: '.format(custom_api_object.take_username([self.user_id])[0], args[0]) + args[1]
                custom_api_object.sender(list(map(lambda x: x[0], groud_sub_id)), message)
                self.send_message('Сообщение отправлено:\n{}'.format(message))

    def take_group_details(self):
        if Tools.is_turtle_privilege(self.user_id):
            args = self.args[0].upper()
            if args in GROUP:
                logging.info('{} отправлен запрос на детализацию по группе {} в чате {}'.format(self.user_id, args, self.peer))
                groud_sub_id = database.Db().select_group(args)
                groud_sub_id = list(map(lambda x: x[0], groud_sub_id))
                message = 'Подписчики группы {}:\n'.format(args)
                user_list, chat_list = [], []

                iterator = 1
                for user in groud_sub_id:
                    if user < 2000000000:
                        user_list.append(user)
                        iterator += 1
                    else:
                        chat_list.append("Беседа №{}".format(str(user)))
                message += '\n'.join(customVkApi(VK_API).take_username(user_list))
                if len(chat_list) > 0:
                    message += '\n\nЧаты:\n'
                    message += '\n'.join(chat_list)
                message += '\n\nВсего людей: {}'.format(str(len(user_list)))
                self.send_message(message)

    def take_user_group(self):
        if Tools.is_turtle_privilege(self.user_id):
            args = self.args[0]
            real_id = VK_API.users.get(user_ids=args)[0]['id']
            user_fullname = customVkApi(VK_API).take_username([real_id])
            logging.info('{} отправлен запрос на детализацию по человеку {} в чате {}'.format(self.user_id, user_fullname[0], self.peer))
            groud_sub_id = database.Db().select_people(real_id)
            groud_sub_id = list(map(lambda x: x[0], groud_sub_id))
            message = 'Группы пользователя {}:\n{}'.format(user_fullname[0], '\n'.join(groud_sub_id))
            self.send_message(message)


    def family_send(self, fam: list, msg: str) -> None:
        prefix = self.command
        keyboard = VkKeyboard(inline=True)
        keyboard.add_button(prefix + fam[0], color='default')
        del fam[0]
        for i in fam:
            keyboard.add_line()
            keyboard.add_button(prefix + i, color='default')
        VK_API.messages.send(peer_id=self.peer, random_id=get_random_id(), keyboard=keyboard.get_keyboard(),
                             message=msg)

    def send_message(self, message: str) -> dict:
        return VK_API.messages.send(
            random_id=get_random_id(),
            peer_id=self.peer,
            message=message)


class Tools:

    @staticmethod
    def get_chat_owner(chat_id: Union[str, int]) -> List[int]:
        """
        Берет админов и владельца чата по айди чата.
        :type peer_id: айди чата
        :return: лист айдишников админов чата (int)
        """
        info = VK_API.messages.getConversationsById(peer_ids=chat_id)
        owner = info['items'][0]['chat_settings']['admin_ids']
        owner.append(info['items'][0]['chat_settings']['owner_id'])
        return owner

    @staticmethod
    def take_keyboardgroup(key_string: str) -> VkKeyboard:
        """
        Отправляет клавиатуру для быстрого вызова команд.
        :param key_string: группа или препод
        :rtype: клавиатура
        """
        keyboard = VkKeyboard()
        keyboard.add_button('Пары ' + key_string, color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Пары на неделю ' + key_string, color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Помощь', color=VkKeyboardColor.POSITIVE)
        return keyboard

    @staticmethod
    def is_turtle_privilege(user_id: int) -> bool:
        """True если user_id имеет роль в Turtle Bot"""
        json_result = VK_API.groups.getMembers(group_id=164805438, filter='managers')
        privilege_user = list(map(lambda x: x['id'], json_result['items']))
        return user_id in privilege_user


class customVkApi:
    def __init__(self, vk_object):
        """
        :type vk_object: ... vk.get_api(), обьект вк после получения доступа по токену.
        """
        self.vk = vk_object

    def take_username_with_chat(self, chat_id: List[int]) -> List[dict]:
        result = []
        user_block = [chat_id[d:d + 26] for d in range(0, len(chat_id), 26)]
        for chat_id in user_block:
            data = []
            for chat in chat_id:
                data.append(str({'peer_id': chat, 'extended': 1}))
            method = 'API.messages.getHistory'
            ready_string = 'return ['
            for user_ready_data in data:
                ready_string += '{}({}),'.format(method, user_ready_data)
            ready_string += '];'
            for user_info in self.vk.execute(code=ready_string):
                user_info = user_info[0]
                result.append({"id": user_info['id'], "FIO": user_info['first_name'] + " " + user_info['last_name'],
                               'online': user_info['online']})
        return result

    def sender(self, chat_id: List[int], message: str) -> bool:
        user_block = [chat_id[d:d + 26] for d in range(0, len(chat_id), 26)]
        for user_id in user_block:
            data = []
            for chat in user_id:
                data.append(str({'user_id': chat, 'random_id': get_random_id(), 'message': 'msg'}))
            var = 'var msg = "{}";\n'.format(message)
            method = 'API.messages.send'
            ready_string = 'return ['
            for user_ready_data in data:
                ready_string += '{}({}),'.format(method, user_ready_data)
            ready_string += '];'
            ready_string = var + ready_string.replace('\'msg\'', 'msg')
            self.vk.execute(code=ready_string)
        return True

    def take_username(self, user: List[int]) -> List[str]:
        resutl_req = self.vk.users.get(user_ids=user)
        user_url = list(map(lambda user_info: '[id{}|{} {}]'.format(user_info['id'], user_info['first_name'],
                                                                    user_info['last_name']), resutl_req))
        return user_url


Command(178431948,178431948,178431948, 'мои стикеры')
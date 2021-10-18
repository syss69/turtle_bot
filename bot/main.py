import logging
import sys
sys.path.append('lib/')
import time
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import command
import setting

logging.basicConfig(filename='app.log',
                    filemode='a',
                    format='%(asctime)s %(levelname)s %(filename)s - %(funcName)s: %(message)s',
                    level=logging.INFO)

# logging.basicConfig(filename='app.log',
#                     filemode='a',
#                     format='%(asctime)s (%(name)s:%(filename)s) %(levelname)s %(funcName)s %(filename)s: %(message)s',
#                     level=logging.INFO)


date = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'восскресенье']
while True:
    try:
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
                if user_id > 0:
                    if "[club164805438|@turtle_bot] " in text.lower():
                        text = text[28:]
                    elif 'action' in event.raw['object']['message'] and event.raw['object']['message']['action'][
                        'type'] == 'chat_invite_user' and \
                            event.raw['object']['message']['action']['member_id'] == -164805438:
                        vk.send_message(random_id=get_random_id(), peer_id=peer,
                                        message='Если Вы меня пригласили, дайте мне доступ к переписке чтобы я мог вам отвечать :)')
                    command.Command(user_id, peer, id, text)

    except Exception as e:
        end_log = str(Exception)
        logging.exception(end_log)
        time.sleep(5)

import datetime
import json
import sqlite3
from typing import List
import mysql.connector
import setting
month = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12

}

schedule_with_class_hour = {
    "13:10  —  14:40": "14:00  —  15:30",
    "15:00  —  16:30": "15:40  —  17:10",
    "16:40  —  18:10": "17:20  —  18:50",
    "18:20  —  19:50": "19:00  —  20:30"
}


class Db:
    """Запросы в удаленную бд"""

    def __init__(self) -> None:
        self.connect = mysql.connector.connect(user=setting.DATABASE['login'],
                                               host=setting.DATABASE['ip'],
                                               database=setting.DATABASE['basename'],
                                               password=setting.DATABASE['password'])

        self.cur = self.connect.cursor(buffered=True)

    def add_subscribe(self, group: str, vk_id: int) -> None:
        self.cur.execute('INSERT INTO subList (groupName, vkID) VALUES (%s,%s)',
                         (group, vk_id,))

    def del_subscribe(self, vk_id: int) -> None:
        self.cur.execute(f'DELETE FROM subList WHERE vkID=%s', (vk_id,))

    def check_duplicate(self, group: str, vk_id: int) -> bool:
        self.cur.execute('SELECT * FROM subList WHERE groupName=%s AND vkID=%s', (group, vk_id,))
        if self.cur.fetchone():
            return True
        else:
            return False

    def select_group(self, group: str) -> list:
        self.cur.execute('SELECT vkID FROM subList WHERE groupName=%s', (group,))
        return self.cur.fetchall()

    def select_people(self, vk_id: int) -> list:
        self.cur.execute('SELECT groupName FROM subList WHERE vkID=%s', (vk_id,))
        return self.cur.fetchall()

    def __del__(self) -> None:
        self.connect.commit()
        self.cur.close()
        self.connect.close()


class DbSchedule:
    """Вызывается через with as, берет расписание с sqlite файла shcedule.sql"""
    def __enter__(self):
        self.connection = sqlite3.connect('schedule.db')
        self.cursor = self.connection.cursor()
        return self

    def cleare_base(self):
        self.cursor.execute('DELETE FROM schedule')

    def append_json_data(self, group: str, json_data: str, is_group: bool):
        self.cursor.execute('INSERT INTO schedule (group_name, json_data, is_group) VALUES (?, ?, ?)',
                            (group, json_data, is_group))

    def select_shcedule(self, command: str) -> dict:
        """Отправка расписания
        :param command: группа или препод по которому надо расписание
        :rtype: json с группами
        """
        result = self.cursor.execute('SELECT * FROM schedule WHERE group_name LIKE ?',
                                     ("{}%".format(command),)).fetchone()

        if result and len(result) > 0 and result[1] != 'null':
            json_string_with_base = dict(json.loads(result[1]))
            base_copy = json_string_with_base.copy()
            for date in base_copy:
                x = date.replace(',', '').split(' ')
                today = datetime.datetime.now()
                current_day = datetime.datetime(day=int(x[0]), month=month[x[1]], year=today.year)
                if datetime.datetime(day=today.day, month=today.month, year=today.year) > current_day:
                    del json_string_with_base[date]
                elif current_day.isocalendar()[1] % 2 != 0 and current_day.isoweekday() == 2:
                    changes_day = {date: {}}
                    for time_apair in base_copy[date]:
                        if time_apair in schedule_with_class_hour:
                            changes_day[date].update(
                                {schedule_with_class_hour[time_apair]: json_string_with_base[date][time_apair]}
                            )
                        else:
                            changes_day[date].update({time_apair: json_string_with_base[date][time_apair]})
                    json_string_with_base.update(changes_day)

            return {'name': result[0].upper(), 'schedule': json_string_with_base}
        else:
            return {'name': None, 'schedule': None}

    def take_group(self) -> List[str]:
        resutl = self.cursor.execute('SELECT group_name FROM schedule WHERE is_group=1').fetchall()
        return list(map(lambda x: x[0], resutl))

    def take_prepods(self) -> List[str]:
        resutl = self.cursor.execute('SELECT group_name FROM schedule WHERE is_group=1').fetchall()
        return list(map(lambda x: x[0], resutl))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.connection.close()


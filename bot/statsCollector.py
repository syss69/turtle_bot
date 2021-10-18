import datetime
import sqlite3


class StatsBase:
    def __init__(self) -> None:
        self.connect = sqlite3.connect('stats.db')
        self.cursor = self.connect.cursor()

    def processed(self, message: str, user_id: int) -> None:
        self.check_exist()
        today = datetime.datetime.now().today()
        day = datetime.datetime.strftime(today, '%d.%m.%Y')
        hour = datetime.datetime.strftime(today, '%H')
        self.cursor.execute('UPDATE statsDay SET processed = processed + 1 WHERE date = ? AND hour = ?', (day, hour))
        self.cursor.execute('INSERT INTO message VALUES (?,?,?,?)', (day, hour, message, user_id))
        self.connect.commit()

    def none_processed(self) -> None:
        self.check_exist()
        today = datetime.datetime.now().today()
        day = datetime.datetime.strftime(today, '%d.%m.%Y')
        hour = datetime.datetime.strftime(today, '%H')
        self.cursor.execute('UPDATE statsDay SET nonProcessed = nonProcessed + 1 WHERE date = ? AND hour = ?',
                            (day, hour))

    def check_exist(self) -> None:
        today = datetime.datetime.now().today()
        day = datetime.datetime.strftime(today, '%d.%m.%Y')
        hour = datetime.datetime.strftime(today, '%H')
        result = self.cursor.execute('SELECT * FROM statsDay WHERE date = ? AND hour = ?', (day, hour))
        if not result.fetchone():
            self.cursor.execute('INSERT INTO statsDay VALUES (?,?,0,0) ', (day, hour))
            self.connect.commit()

    def return_result(self) -> dict:
        today = datetime.datetime.now().today()
        day = datetime.datetime.strftime(today, '%d.%m.%Y')
        hour = datetime.datetime.strftime(today, '%H')
        return self.cursor.execute('SELECT * FROM statsDay WHERE date = ? AND hour = ?', (day, hour)).fetchone()

    def __del__(self) -> None:
        self.connect.commit()
        self.cursor.close()
        self.connect.close()


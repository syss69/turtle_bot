import requests
import json
import datetime


class API:
    def __init__(self):
        self.addres = 'http://45.155.207.232/api/v1/'

    def take_schedule(self) -> dict:
        self.addres += 'take/'
        return requests.get(self.addres + 'schedule').json()

    def take_apair_group(self) -> dict:
        self.addres += 'take/'
        return requests.get(self.addres + 'apairgroup').json()

    def take_apair_prepods(self) -> dict:
        self.addres += 'take/'
        return requests.get(self.addres + 'apairprepods').json()

    def take_list_group(self) -> list:
        self.addres += 'take/'
        x = []
        for groupName in requests.get(self.addres + 'apairgroup').json():
            x.append(groupName)
        return x

    def take_list_prepods_family(self) -> list:
        self.addres += 'take/'
        x = []
        for groupName in requests.get(self.addres + 'apairprepods').json():
            groupName = groupName.split(' ')[0]
            if groupName not in x:
                x.append(groupName)
        return x

    def take_list_prepods(self) -> list:
        self.addres += 'take/'
        x = []
        for groupName in requests.get(self.addres + 'apairprepods').json():
            x.append(groupName)
        return x

    def take_current_apair_group(self, group: str) -> dict:
        self.addres += 'take/'
        return requests.get(self.addres + 'selectapairgroup', params={'group': group.upper()}).json()

    def take_current_apair_teatcher(self, family: str) -> dict:
        self.addres += 'take/'
        return requests.get(self.addres + 'selectapairprepods', params={'teatcher': family.title()}).json()

from typing import *


def distance_leven(first_args: str, two_args: str) -> int:
    distance = 0

    len_finded = len(first_args)
    len_family = len(two_args)

    if len_finded != len_family:
        distance = abs(len_finded - len_family)

    if len_family < len_finded:
        max_symbol = len_family
    else:
        max_symbol = len_finded

    for numChar in range(max_symbol):
        if first_args[numChar] != two_args[numChar]:
            distance += 1
    return distance


class People:
    def __init__(self, family: str, first_name: str, last_name: str, smile: str = ''):
        self.first_name = first_name
        self.family = family
        self.last_name = last_name
        self.full_name = "{} {} {} {}".format(family, first_name, last_name, smile)


class Prepods:
    prepods_list = []

    @classmethod
    def create_prepods(self, *args):
        self.prepods_list.append(People(*args))

    @classmethod
    def find_people(self, need_family: str) -> List[People]:
        find = list(filter(lambda x: x.family == need_family, self.prepods_list))
        if find.__len__() == 0:
            for family in self.prepods_list:
                if distance_leven(need_family, family.family) <= 2:
                    find.append(family)
        return find

    @classmethod
    def add_perpods(self, family: str, name: str, two_name: str) -> bool:
        with open('prepodBase.txt', 'a') as f:
            f.write("{} {} {}\n".format(family, name, two_name))
        self.create_prepods(name, family, two_name)
        return True

    @classmethod
    def import_prepods(self, file):
        with open(file, 'r', encoding="utf-8") as f:
            iterator = f.read().split('\n')
            for i in iterator:
                i = i.split(' ')
                if i.__len__() > 1:
                    self.create_prepods(*i)
        return self.prepods_list

Prepods.import_prepods('prepodBase.txt')


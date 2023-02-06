from imports.imports import *
import parser.homework
import database.sql_commands


def get_schedule(userid: str) -> str or bool:
    sp: dict = parser.homework.get_all_homework(userid, delta=7)
    if type(sp) != dict:
        return False
    day_week = {"__*_Понедельник_*__": 1,
                "__*_Вторник_*__": 2,
                "__*_Среда_*__": 3,
                "__*_Четверг_*__": 4,
                "__*_Пятница_*__": 5,
                "__*_Суббота_*__": 6,
                "__*_Воскресенье_*__": 7}
    dictionary = {}
    notes = get_schedule_notes(userid)
    for key in sp:
        day = key.split()[0]
        for i in range(len(sp[key])):
            try:
                sp[key][i] = ' '.join(sp[key][i][:-1]) + '\n' + notes[day_week[day]][sp[key].index(sp[key][i]) + 1]
            except KeyError:
                sp[key][i] = ' '.join(sp[key][i][:-1])
        dictionary[day] = ['\n'.join(sp[key])]
    dictionary = dict(sorted(dictionary.items(), key=lambda x: day_week[x[0]]))

    send = []
    for key in dictionary:
        send += [key + '\n' + dictionary[key][0]]
    return "\n\n".join(send)


def get_schedule_notes(userid: str) -> dict:
    notes = database.sql_commands.get_notes_schedule(userid)
    f = {}
    for i in range(len(notes)):
        note = notes[i]
        if note[0] in f:
            f[note[0]][note[1]] = note[2]
        else:
            f[note[0]] = {note[1]: note[2]}
    return f

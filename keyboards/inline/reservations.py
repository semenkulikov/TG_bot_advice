import datetime

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.models import Timetable


def advice_markup():
    """ Inline buttons для выбора режима записи на прием """
    actions = InlineKeyboardMarkup(row_width=1)
    actions.add(InlineKeyboardButton(text=f"Онлайн прием", callback_data="Online"))
    actions.add(InlineKeyboardButton(text=f"Личный прием", callback_data="Home"))
    actions.add(InlineKeyboardButton(text=f"Выйти", callback_data="Exit"))
    return actions

def get_date_markup(online_advice=True) -> InlineKeyboardMarkup:
    """
    Inline кнопки для выбора даты записи на прием
    :param online_advice: Режим приема - онлайн или личный
    :return: InlineKeyboardMarkup
    """
    # Получение текущей даты, получение существующих дат из БД.

    cur_datetime = datetime.datetime.now()
    existing_dates = list()
    for timetable_obj in Timetable.select().where(Timetable.date >= cur_datetime.date()):
        if timetable_obj.date == cur_datetime.date():
            if timetable_obj.start_time.hour >= cur_datetime.time().hour:
                if (online_advice is False and timetable_obj.date.weekday() in (2, 3, 4, 5) or
                        online_advice is True and timetable_obj.date.weekday() in (0, 1)):
                    existing_dates.append(timetable_obj.date)
        else:
            if (online_advice is False and timetable_obj.date.weekday() in (2, 3, 4, 5) or
                    online_advice is True and timetable_obj.date.weekday() in (0, 1)):
                existing_dates.append(timetable_obj.date)
    # Сортировка списка объектов Timetable по возрастанию даты и удаление дублирующихся записей
    existing_dates = sorted(list(set(existing_dates)))


    keyboard = InlineKeyboardMarkup(row_width=2)
    for i, date_obj in enumerate(existing_dates):
        keyboard.add(InlineKeyboardButton(text=date_obj.strftime("%d.%m.%Y"),
                                          callback_data=date_obj.strftime("%Y-%m-%d")))

    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="Cancel"))
    return keyboard

def get_time_markup(date_selected, free_time_list) -> InlineKeyboardMarkup:
    """
    Inline кнопки для выбора времени записи на прием
    :param free_time_list: Список свободных объектов Timetable
    :param date_selected: Дата, на которую производится выбор времени
    :return: InlineKeyboardMarkup
    """

    keyboard = InlineKeyboardMarkup(row_width=3)
    my_row = list()
    for index, time_obj in enumerate(free_time_list, start=1):
        button = InlineKeyboardButton(text=time_obj,
                                          callback_data=f"({date_selected.split("-")[-1]}) {time_obj}")
        my_row.append(button)
        if index % 3 == 0:
            keyboard.add(*my_row)
            my_row = []
    if my_row:
        keyboard.add(*my_row)
    return keyboard


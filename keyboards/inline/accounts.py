from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from config_data.config import ADMIN_ID
from database.models import User, Timetable


def users_markup():
    """ Inline buttons для выбора юзера """
    users_obj = User.select()
    actions = InlineKeyboardMarkup(row_width=2)

    for user in users_obj:
        if int(user.user_id) != int(ADMIN_ID):
            actions.add(InlineKeyboardButton(text=f"{user.full_name}", callback_data=user.id))
    actions.add(InlineKeyboardButton(text=f"Выйти", callback_data="Exit"))
    return actions


def users_data_markup():
    """ Inline buttons для выбора типа отправляемых данных """

    actions = InlineKeyboardMarkup(row_width=2)
    actions.add(InlineKeyboardButton(text=f"Номер телефона", callback_data="Contact"))
    actions.add(InlineKeyboardButton(text=f"Дату рождения", callback_data="Birthdate"))
    return actions

def get_timetables_markup(user_id: int):
    """ Inline buttons для отображения текущих записей пользователя """
    cur_user = User.get_by_id(user_id)

    # Получаем все записи Timetable пользователя
    timetables = Timetable.select().where(Timetable.user_id == cur_user, Timetable.is_booked == True)

    keyboard = InlineKeyboardMarkup(row_width=2)
    for elem in timetables:
        keyboard.add(InlineKeyboardButton(text=f"{elem.date.strftime("%d.%m")} ({elem.start_time.strftime("%H:%M")} "
                                               f"- {elem.end_time.strftime("%H:%M")})",
                                          callback_data=str(elem.id)))

    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="Cancel"))
    return keyboard

def delete_timetable_markup():
    """ Inline button для удаления конкретной записи пользователя """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="Cancel_"),
                 InlineKeyboardButton(text="Удалить", callback_data="Delete"))
    return keyboard
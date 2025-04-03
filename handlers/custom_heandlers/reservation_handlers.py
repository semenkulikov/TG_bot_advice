import datetime
import json
import threading

from telebot.types import Message

from database.models import User, Timetable
from keyboards.inline.reservations import advice_markup, get_date_markup, get_time_markup
from loader import app_logger, bot
from config_data.config import ADMIN_ID, ALLOWED_USERS
from states.states import ReservationStates
from utils.functions import send_notification


@bot.message_handler(commands=["get_reservation"])
def advice_handler(message: Message):
    """ Хендлер для записи на прием """
    app_logger.info(f"Запрос на прием от {message.from_user.full_name}")

    # Отправка inline клавиатуры для выбора режима приема
    message_id = bot.send_message(message.from_user.id, "Выберите режим приема:", reply_markup=advice_markup()).id
    # Сохраняем id сообщения для дальнейшего удаления
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data[message.from_user.id] = message_id

    bot.set_state(message.from_user.id, ReservationStates.get_mode)


@bot.callback_query_handler(func=None, state=ReservationStates.get_mode)
def reservation_date_handler(call):
    """
    Callback хендлер для бронирования определенного времени для консультации.
    """
    bot.answer_callback_query(callback_query_id=call.id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        cur_message_id = data[call.from_user.id]
        bot.delete_message(call.message.chat.id, cur_message_id)

        if call.data in "Online":
            app_logger.info(f"Запрос бронирования времени на онлайн прием от {call.from_user.full_name}")
            bot.send_message(call.message.chat.id, "Вы записываетесь на онлайн консультацию. "
                                              "Она проходит по понедельникам и вторникам с 17:00 до 22:00.")
            online_advice = True
        elif call.data in "Home":
            app_logger.info(f"Запрос бронирования времени на личный прием от {call.from_user.full_name}")
            bot.send_message(call.message.chat.id, "Вы записываетесь на личную консультацию. "
                                              "Она проходит со среды по субботу с 14:00 до 18:00.")
                                                   # "Она проходит каждый день с 14:00 до 18:00")
            online_advice = False
        else:
            # bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            # return
            bot.send_message(call.message.chat.id, "Вы вернулись в главное меню.")
            app_logger.info(f"Пользователь {call.from_user.full_name} вернулся в главное меню")
            bot.set_state(call.message.chat.id, None)
            data[call.from_user.id] = None
            return


        # Отправляет пользователю клавиатуру с выбором даты.
        app_logger.info(f"Отправка клавиатуры с датами для бронирования консультации {call.from_user.full_name}")
        message_id = bot.send_message(call.message.chat.id, "Выберите дату:",
                                      reply_markup=get_date_markup(online_advice=online_advice)).id
        bot.set_state(call.message.chat.id, ReservationStates.get_date)

        data[call.from_user.id] = message_id


@bot.callback_query_handler(func=None, state=ReservationStates.get_date)
def reservation_time_handler(call):
    """ Хендлер для бронирования определенного времени в конкретную дату для консультации. """
    bot.answer_callback_query(callback_query_id=call.id)

    if call.data in "Cancel":
        bot.send_message(call.message.chat.id, "Вы вернулись в главное меню.")
        app_logger.info(f"Пользователь {call.from_user.full_name} вернулся в главное меню")
        bot.set_state(call.message.chat.id, None)
        return

    app_logger.info(f"Запрос бронирования времени от {call.from_user.full_name} на дату {call.message.text}")

    # Получение свободных часов консультаций по дате из БД.
    cur_time = datetime.datetime.now()
    free_times = []
    for timetable in Timetable.select().where(Timetable.date == call.data,
                                              Timetable.is_booked == False,
                                              ):
        if timetable.date == cur_time.date():
            if timetable.start_time.hour >= cur_time.time().hour:
                free_times.append(f"{timetable.start_time.strftime("%H:%M")} - {timetable.end_time.strftime("%H:%M")}")
        else:
            free_times.append(f"{timetable.start_time.strftime("%H:%M")} - {timetable.end_time.strftime("%H:%M")}")

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        cur_message_id = data[call.from_user.id]
        if cur_message_id is not None:
            bot.delete_message(call.message.chat.id, cur_message_id)

        if not free_times:
            app_logger.warning(f"Внимание! Нет свободных часов для бронирования консультации "
                               f"на {call.message.text} от {call.from_user.full_name}")
            # Отправка уведомления пользователю
            bot.send_message(call.message.chat.id,
                             "К сожалению, нет свободных часов для бронирования консультации на эту дату.")
            bot.set_state(call.message.chat.id, None)

            data[call.from_user.id] = None
            return

        app_logger.info(f"Отправка клавиатуры с временами для бронирования консультации {call.from_user.full_name}")
        message_id = bot.send_message(call.message.chat.id, "Выберите время:",
                         reply_markup=get_time_markup(call.data, free_times)).id
        data[call.from_user.id] = message_id

        bot.set_state(call.message.chat.id, ReservationStates.get_time)


@bot.callback_query_handler(func=None, state=ReservationStates.get_time)
def reservation_handler(call):
    """ Хендлер для бронирования консультации. """

    bot.answer_callback_query(callback_query_id=call.id)

    cur_user = User.get_or_none(User.user_id == call.from_user.id)
    app_logger.info(f"Запрос бронирования консультации от {cur_user.full_name} на дату {call.data}")

    # Извлечение дня, стартовой даты и конечной даты из поля datetime_reserved
    day, times = call.data.split(" ", maxsplit=1)
    start_time, end_time = times.split(" - ")
    day = day[1:-1]

    # Поиск и получение всех объектов Timetable с данными датами начала и конца.
    timetables = Timetable.select().where(Timetable.start_time == start_time,
                                         Timetable.end_time == end_time,
                                         Timetable.is_booked == False)
    cur_t = None
    for t in timetables:
        # Проверка, что день содержится в дате
        if str(t.date.day) in day:
            cur_t = t
            break

    # Если профиль пользователя не содержит телефон, или ему меньше 21 года, то блокируем
    # if user.phone is None:
    #     app_logger.warning(f"Внимание! Запрос бронирования консультации от {user.full_name} "
    #                        f"на {datetime_reserved} отклонен: нет телефона")
    #     vk_api_elem.messages.send(peer_id=user_id,
    #                               message="Пожалуйста, укажите ваш номер телефона для того, чтобы мы могли выслать напоминание о времени вашей записи!\n"
    #                                       "Напишите ваш номер телефона в формате: +79991234567",
    #                               random_id=get_random_id(),
    #                               keyboard=KEYBOARD)
    #     return
    # elif user.birthday is None:
    #     app_logger.warning(f"Внимание! Запрос бронирования консультации от {user.full_name} "
    #                        f"на {datetime_reserved} отклонен: не указан день рождения")
    #     vk_api_elem.messages.send(peer_id=user_id,
    #                               message="Бронирование не удалось: не указан день рождения!\n"
    #                                       "Напишите ваш день рождения в формате: 12.13.1415 (день, месяц, год)",
    #                               random_id=get_random_id(),
    #                               keyboard=KEYBOARD)
    #     return
    # user_birthday_list = [int(elem) for elem in user.birthday.split(".")]
    # user_birthday = datetime.date(year=user_birthday_list[2], month=user_birthday_list[1],
    #                               day=user_birthday_list[0])
    # if (datetime.datetime.now().date() - user_birthday).days <= 7665:
    #     app_logger.warning(f"Внимание! Запрос бронирования консультации от {user.full_name} "
    #                        f"на {datetime_reserved} отклонен: менее 21 года")
    #     vk_api_elem.messages.send(peer_id=user_id,
    #                               message="Бронирование не удалось: вы должны быть старше 21 года!",
    #                               random_id=get_random_id(),
    #                               keyboard=KEYBOARD)
    #     return
    # Присвоение найденному Timetable объекту user_id и изменение поля is_booked


    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        cur_message_id = data[call.from_user.id]
        if cur_message_id is not None:
            bot.delete_message(call.message.chat.id, cur_message_id)
            data[call.from_user.id] = None

    if cur_t is not None:
        cur_t.user_id = cur_user.id
        cur_t.is_booked = True
        cur_t.save()
        app_logger.info(f"Бронирование консультации успешно завершено от {cur_user.full_name} на {cur_t.date}")
        # Отправка уведомления пользователю
        bot.send_message(call.message.chat.id, f"Вы записаны на консультацию!\n"
                                            f"Ваше время: {start_time} - {end_time}\n"
                                            f"Дата: {cur_t.date}\n")
        if cur_user.phone is None:
            bot.send_message(call.message.chat.id, f"Если оставите номер своего телефона - "
                                              f"мы вышлем вам напоминание о времени записи, для вашего удобства!")
        else:
            bot.send_message(call.message.chat.id, f"Мы отправим вам напоминание о времени "
                                            f"вашей записи за 2 часа до начала приема!")

        # Запуск напоминания о консультации за 2 часа до начала консультации
        send_notification(cur_t.id)
        # Отправка уведомления администратору о бронировании
        app_logger.info(f"Отправка уведомления администратору о новом бронировании консультации")
        for admin_id in ALLOWED_USERS:
            if admin_id != int(ADMIN_ID):
                bot.send_message(admin_id, f"Новое бронирование консультации:\n"
                                          f"Пользователь: {cur_user.full_name}\n"
                                          f"Номер телефона: {cur_user.phone}\n"
                                          f"Дата рождения: {cur_user.birthday}\n"
                                          f"Время: {start_time} - {end_time}\n"
                                          f"Дата: {cur_t.date}\n")
        bot.set_state(call.message.chat.id, None)

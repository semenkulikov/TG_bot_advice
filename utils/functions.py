import datetime
import threading

from database.models import Timetable, User
from loader import app_logger, bot


def send_notification(timetable_id: int):
    """ Функция для создания асинхронного потока для отправки уведомлений через библиотеку schedule
    :param timetable_id: идентификатор бронирования объекта Timetable.
    """
    app_logger.info(f"Запуск асинхронного потока для отправки уведомления.")
    timetable = Timetable.get_by_id(timetable_id)
    user = User.get_by_id(timetable.user_id)
    consultation_datetime = datetime.datetime.combine(timetable.date, timetable.start_time)
    cur_datetime = datetime.datetime.now()

    # Вычисление точной даты: за день до приема до начала консультации previous_day вида 2025-10-01
    previous_day = timetable.date - datetime.timedelta(days=1)
    notification_datetime_previous_day = datetime.datetime.combine(previous_day, datetime.time(hour=9, minute=0))
    notification_datetime_current_day = datetime.datetime.combine(timetable.date, datetime.time(hour=9, minute=0))
    # Вычисление точной даты и времени: за два часа до начала консультации notification_datetime вида 2025-10-01 18:00
    notification_datetime_0 = (datetime.datetime.combine(timetable.date, timetable.start_time) -
                             datetime.timedelta(hours=2))


    # Создание асинхронных потоков таймеров.
    if consultation_datetime.time().hour >= 12:
        if datetime.datetime.now().date() < notification_datetime_previous_day.date():
            threading.Timer((notification_datetime_previous_day - cur_datetime).total_seconds(),
                            send_notification_message,
                            args=(user, consultation_datetime)).start()
            app_logger.info(f"Запланировано отправление уведомления {user.full_name} на "
                            f"{notification_datetime_previous_day}")

        threading.Timer((notification_datetime_current_day - cur_datetime).total_seconds(),
                        send_notification_message,
                        args=(user, consultation_datetime)).start()
        app_logger.info(f"Запланировано отправление уведомления {user.full_name} на "
                        f"{notification_datetime_current_day}")
    if notification_datetime_0 != notification_datetime_current_day:
        threading.Timer((notification_datetime_0 - cur_datetime).total_seconds(),
                        send_notification_message,
                        args=(user, consultation_datetime)).start()
        app_logger.info(f"Запланировано отправление уведомления {user.full_name} на "
                        f"{notification_datetime_0}")

    # В качестве теста отправляю уведомление через 5 секунд
    threading.Timer(5, send_notification_message, args=(user, consultation_datetime)).start()

def send_notification_message(user: User, consultation_datetime):
    """ Функция для отправки уведомления пользователю
    :param user: объект пользователя
    :param consultation_datetime: время консультации
    """
    app_logger.info(f"Отправка уведомления пользователю {user.full_name}")
    bot.send_message(user.user_id, f"Напоминание!\nУ вас есть консультация на {consultation_datetime}.")

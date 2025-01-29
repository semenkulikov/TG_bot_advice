import datetime
import os
import threading
from time import sleep
import peewee

from config_data.config import BASE_DIR
from loader import app_logger

db = peewee.SqliteDatabase(os.path.join(BASE_DIR, "database/database.db"))


class BaseModel(peewee.Model):
    """ Базовая модель """
    class Meta:
        database = db


class User(BaseModel):
    """ Модель пользователя """
    user_id = peewee.CharField(unique=True)
    full_name = peewee.CharField()
    username = peewee.CharField()
    is_premium = peewee.BooleanField(null=True)
    phone = peewee.CharField(null=True)
    birthday = peewee.DateField(null=True)


class Group(BaseModel):
    """ Класс группы """
    group_id = peewee.CharField(unique=True)
    title = peewee.CharField()
    description = peewee.TextField(null=True)
    bio = peewee.TextField(null=True)
    invite_link = peewee.CharField(null=True)
    location = peewee.CharField(null=True)
    username = peewee.CharField(null=True)


class Timetable(BaseModel):
    """ Модель для расписания графика свободных часов """
    user_id = peewee.ForeignKeyField(User, backref="timetables", null=True)
    date = peewee.DateField(null=False)
    start_time = peewee.TimeField(null=False)
    end_time = peewee.TimeField(null=False)
    is_booked = peewee.BooleanField(default=False)


def create_models():
    db.create_tables(BaseModel.__subclasses__())


def create_time_tables(start_date: datetime.date, end_date: datetime.date):
    """ Функция для генерирования графика расписания консультаций на неделю. """
    # cur_datetime = datetime.datetime.now()

    # Удаление более ранних записей
    delete_time_tables()

    timedelta_days = (end_date - start_date).days
    for i in range(timedelta_days):
        cur_date = start_date + datetime.timedelta(days=i)
        if cur_date.weekday() not in [6]:  # Будни, кроме выходных
            if cur_date.weekday() in (0, 1):  # Понедельник, вторник - онлайн прием
                for start_time in [# "10:00", "10:20", "10:40", "11:00", "11:20", "11:40",
                                   # "14:00", "14:20", "14:40", "15:00", "15:20", "15:40",
                                   # "16:00", "16:20", "16:40",
                                    "17:00", "17:20", "17:40", "18:00", "18:20", "18:40",
                                    "19:00", "19:20", "19:40", "20:00", "20:20", "20:40",
                                    "21:00", "21:20", "21:40"]:
                    end_time = start_time.split(":")[0] + ":" + str(int(start_time.split(":")[1]) + 19)
                    # Проверка, нет ли уже существующей записи
                    if not Timetable.select().where(Timetable.date == cur_date,
                                                    Timetable.start_time == start_time,
                                                    Timetable.end_time == end_time).exists():
                        Timetable.create(date=cur_date, start_time=start_time, end_time=end_time)
            elif cur_date.weekday() in (2, 3, 4, 5):  # Среда, четверг, пятница и суббота - офлайн прием
                for start_time in [# "13:00", "13:20", "13:40",
                                   "14:00", "14:20", "14:40",
                                   "15:00", "15:20", "15:40", "16:00", "16:20", "16:40",
                                   "17:00", "17:20", "17:40"]: # "18:00", "18:20", "18:40"]:
                    end_time = start_time.split(":")[0] + ":" + str(int(start_time.split(":")[1]) + 19)
                    if not Timetable.select().where(Timetable.date == cur_date,
                                                    Timetable.start_time == start_time,
                                                    Timetable.end_time == end_time).exists():
                        Timetable.create(date=cur_date, start_time=start_time, end_time=end_time)

def delete_time_tables():
    """ Функция для удаления старых устаревших записей графика (вчерашних и ранее) """
    cur_datetime = datetime.datetime.now()
    Timetable.delete().where(Timetable.date < cur_datetime.date()).execute()

#
#
# def generate_time_tables():
#     """ Функция для асинхронного запуска create_time_tables каждую неделю """
#     while True:
#         app_logger.info("Генерация графика расписания консультаций и удаление старых записей...")
#         threading.Timer(24 * 60 * 60, delete_time_tables).start()
#         threading.Timer(24 * 60 * 60, create_time_tables).start()
#         sleep(24 * 60 * 60)
#
# def start_generate():
#     """ Запуск генерации графика расписания консультаций в фоновом режиме """
#     delete_time_tables()
#     create_time_tables()
#     threading.Thread(target=generate_time_tables).start()
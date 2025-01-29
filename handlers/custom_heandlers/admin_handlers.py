import datetime

from telebot.types import Message

from config_data.config import ALLOWED_USERS
from database.models import User, Timetable
from keyboards.inline.accounts import users_markup
from loader import bot, app_logger, calendar, calendar_callback
from states.states import AdminPanel


@bot.message_handler(commands=["admin_panel"])
def admin_panel(message: Message):
    if message.from_user.id in ALLOWED_USERS:
        app_logger.info(f"Администратор {message.from_user.full_name} зашел в админ панель.")
        bot.send_message(message.from_user.id, "Админ панель")
        bot.send_message(message.from_user.id, "Все пользователи базы данных:", reply_markup=users_markup())
        bot.set_state(message.from_user.id, AdminPanel.get_users)
    else:
        bot.send_message(message.from_user.id, "У вас недостаточно прав")
        app_logger.warning(f"Пользователь {message.from_user.full_name} попытался зайти в админ панель.")


@bot.callback_query_handler(func=None, state=AdminPanel.get_users)
def get_user(call):
    bot.answer_callback_query(callback_query_id=call.id)
    if call.data == "Exit":
        bot.send_message(call.message.chat.id, "Вы успешно вышли из админ панели.")
        bot.set_state(call.message.chat.id, None)
    else:
        user_obj: User = User.get_by_id(call.data)
        bot.send_message(call.message.chat.id, f"Имя: {user_obj.full_name}\n"
                                               f"Телеграм: @{user_obj.username}\n")


@bot.message_handler(commands=["get_report"])
def get_report_handler(message: Message):
    """ Админ хендлер для отправки отчета о записях на консультации """
    if message.from_user.id in ALLOWED_USERS:
        app_logger.info(f"Запрос на отчет о записях на консультации от администратора {message.from_user.full_name}")

        # Отправка отчета о записях на консультации
        bot.send_message(message.from_user.id, "Отчет о записях на консультации:")

        report_text = "Отчет о консультациях на сегодня:\n\n"
        # Получаем все записи Timetable на сегодня.
        today_timetables = Timetable.select().where(Timetable.is_booked == True)
        cur_date = datetime.date.today()
        for timetable in today_timetables:
            if timetable.date != cur_date:
                report_text += f"\nДата: {timetable.date}\n\n"
                cur_date = timetable.date
            cur_user: User = User.get_by_id(timetable.user_id)
            report_text += (
                f"Время: {timetable.start_time.strftime("%H:%M")} - {timetable.end_time.strftime("%H:%M")}\n"
                f"Имя: {cur_user.full_name}\n"
                f"Телефон: {cur_user.phone}\n"
                f"Дата рождения: {cur_user.birthday}\n\n")

        bot.send_message(message.from_user.id, report_text)
        bot.send_message(message.from_user.id, f"Всего записей: {len(today_timetables)}")

    else:
        bot.send_message(message.from_user.id, "У вас недостаточно прав")
        app_logger.warning(f"Пользователь {message.from_user.full_name} попытался запросить отчет!")


@bot.message_handler(commands=["run_generating"])
def get_report_handler(message: Message):
    """ Админ хендлер для отправки отчета о записях на консультации """
    if message.from_user.id in ALLOWED_USERS:
        app_logger.info(f"Запрос на генерацию расписания от администратора {message.from_user.full_name}")
        with bot.retrieve_data(message.from_user.id, message.chat.id) as user_data:
            user_data[str(message.chat.id)] = {"start_date": None, "end_date": None}

            bot.send_message(
                message.chat.id,
                "Выберите дату начала:",
                reply_markup=calendar.create_calendar(name=calendar_callback.prefix),
            )
    else:
        bot.send_message(message.from_user.id, "У вас недостаточно прав")
        app_logger.warning(f"Пользователь {message.from_user.full_name} попытался сгенерировать расписание!")

# Обработчик inline-кнопок календаря
@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_callback.prefix))
def handle_calendar_callback(call):
    chat_id = call.message.chat.id
    name, action, year, month, day = call.data.split(calendar_callback.sep)
    date = calendar.calendar_query_handler(bot, call, name, action, year, month, day)

    with bot.retrieve_data(call.from_user.id, call.from_user.id) as user_data:
        if action == "DAY":
            if user_data[chat_id]["start_date"] is None:
                # Пользователь выбирает дату начала
                user_data[chat_id]["start_date"] = date
                bot.send_message(
                    chat_id,
                    f"Дата начала: {date.strftime('%d.%m.%Y')}\nТеперь выберите дату конца:",
                    reply_markup=calendar.create_calendar(name=calendar_callback.prefix),
                )
            else:
                # Пользователь выбирает дату конца
                if date >= user_data[chat_id]["start_date"]:
                    user_data[chat_id]["end_date"] = date
                    bot.send_message(
                        chat_id,
                        f"Дата конца: {date.strftime('%d.%m.%Y')}\n"
                        f"Период выбран: {user_data[chat_id]['start_date'].strftime('%d.%m.%Y')}"
                        f" - {date.strftime('%d.%m.%Y')}",
                    )
                    # Сброс данных после выбора
                    user_data[chat_id] = {"start_date": None, "end_date": None}
                else:
                    bot.send_message(
                        chat_id,
                        "Дата конца не может быть раньше даты начала. Попробуйте снова.",
                        reply_markup=calendar.create_calendar(name=calendar_callback.prefix),
                    )

        elif action == "CANCEL":
            bot.send_message(chat_id, "Отменено.")
            user_data[chat_id] = {"start_date": None, "end_date": None}
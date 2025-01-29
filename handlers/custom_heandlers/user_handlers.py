import datetime

from telebot.types import Message

from config_data.config import ALLOWED_USERS
from database.models import User, Timetable
from keyboards.inline.accounts import users_markup, get_timetables_markup, delete_timetable_markup
from loader import bot, app_logger
from states.states import AdminPanel, TimetablesStates


@bot.message_handler(commands=["get_often_questions"])
def faq_handler(message: Message):

    # Получение объекта пользователя из БД.
    user = User.get_or_none(User.user_id == message.from_user.id)
    app_logger.info(f"Запрос ответов на вопросы от {user.full_name}.")

    result_text = """1. Что можно с собой принести на прием? — Вы можете принести с собой одну фотографию человека, о котором хотите узнать.\n
2. Сколько длиться прием? — Длительность сессии составляет около 20 минут.\n
3. По какому адресу идет прием? — г. Магнитогорск, ул. Жукова, д. 17, отдельный вход рядом с подъездом №1.\n
4. Я беременна, могу я прийти на прием? — Да, я работаю с белой магией, это безопасно для женщин в положении.\n
5. Какова стоимость приема? — Вы оплачиваете мою работу, суммой на свое усмотрение.\n
6. Могу ли я привести с собой на прием несовершеннолетнего ребенка? — Да, в вашем присутствии я могу посмотреть здоровье ребенка.\n
7. Можете ли вы предсказать будущее? — Да, я могу увидеть основные линии развития жизни.\n
8. Можете ли вы помочь избавиться от алкогольной или другой зависимости? — Да, в большинстве случаев результат положительный.
    """
    bot.send_message(message.chat.id, result_text, parse_mode="Markdown")


@bot.message_handler(commands=["my_advices"])
def my_timetables_handler(message: Message):
    """ Хендлер для управления записями пользователя """
    user = User.get(User.user_id == message.from_user.id)
    app_logger.info(f"Пользователь {user.full_name} зашел в управление записями.")
    bot.send_message(message.from_user.id, "Вот ваши текущие записи:", reply_markup=get_timetables_markup(user.id))
    bot.set_state(message.from_user.id, TimetablesStates.get_obj)


@bot.callback_query_handler(func=None, state=TimetablesStates.get_obj)
def reservation_handler(call):
    """ Хендлер для выдачи информации по объекту Timetable """

    bot.answer_callback_query(callback_query_id=call.id)

    if call.data == "Cancel":
        bot.send_message(call.from_user.id, "Вы вернулись в главное меню")
        bot.set_state(call.from_user.id, None)
    else:
        cur_timetable_obj: Timetable = Timetable.get_by_id(call.data)
        app_logger.info(f"Пользователь {call.from_user.full_name} получил информацию о записи ID={cur_timetable_obj.id}")  # noqa

        with bot.retrieve_data(call.message.chat.id, call.from_user.id) as data:
            data["cur_timetable_id"] = cur_timetable_obj.id  # noqa

        bot.send_message(call.from_user.id, f"Информация о записи:\n"
                                          f"Дата: {cur_timetable_obj.date.strftime('%d.%m')}\n"
                                          f"Время: c {cur_timetable_obj.start_time.strftime('%H:%M')} до "
                                          f"{cur_timetable_obj.end_time.strftime('%H:%M')}",
                         reply_markup=delete_timetable_markup())
        bot.set_state(call.from_user.id, TimetablesStates.delete_obj)


@bot.callback_query_handler(func=None, state=TimetablesStates.delete_obj)
def reservation_handler(call):
    """ Хендлер для для удаления Timetable объекта """

    bot.answer_callback_query(callback_query_id=call.id)
    user = User.get(User.user_id == call.from_user.id)
    if call.data == "Cancel_":
        bot.send_message(call.from_user.id, "Выберите запись для просмотра:",
                         reply_markup=get_timetables_markup(user.id))
        bot.set_state(call.from_user.id, TimetablesStates.get_obj)
    elif call.data == "Delete":
        with bot.retrieve_data(call.message.chat.id, call.from_user.id) as data:
            cur_timetable_id = data["cur_timetable_id"]
            cur_timetable_obj: Timetable = Timetable.get_by_id(cur_timetable_id)

            app_logger.info(f"Пользователь {call.from_user.full_name} удалил запись на "
                            f"{cur_timetable_obj.date.strftime("%d.%m.%Y")} (ID: {cur_timetable_obj.id})")
            cur_timetable_obj.delete_instance()
            bot.send_message(call.from_user.id, "Запись отменена!")

import datetime

from telebot.types import Message

from config_data.config import ALLOWED_USERS
from database.models import User, Timetable
from keyboards.inline.accounts import users_markup
from loader import bot, app_logger
from states.states import AdminPanel


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
def my_advices_handler(message: Message):
    """ Хендлер для управления записями пользователя """
    bot.send_message(message.from_user.id, "Эта функция еще в разработке")


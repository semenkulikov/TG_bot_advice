from telebot.types import Message

from database.models import User
from keyboards.inline.accounts import users_data_markup
from keyboards.reply.handlers_reply import send_phone_reply
from loader import bot, app_logger
from states.states import UsersDataStates


@bot.message_handler(commands=["send_data"])
def get_users_data_handler(message: Message):
    """ Хендлер для отправки данных пользователя """
    app_logger.info(f"Пользователь {message.from_user.full_name} отправляет свои данные...")
    bot.send_message("Какие данные вы хотите добавить?", reply_markup=users_data_markup())
    bot.set_state(message.from_user.id, UsersDataStates.get_data_state)


@bot.callback_query_handler(func=None, state=UsersDataStates.get_data_state)
def get_data_handler(call):
    """ Хендлер для дальнейшего распределения ввода пользовательских данных """
    bot.answer_callback_query(callback_query_id=call.id)
    if call.data == "Contact":
        bot.send_message(call.from_user.id, "Нажмите на кнопку ниже", reply_markup=send_phone_reply())


@bot.message_handler(content_types=["contact"])
def get_phone_handler(message: Message):
    """ Хендлер для получения номера телефона """

    phone_number = message.contact.phone_number
    cur_user = User.get(User.user_id == message.from_user.id)
    cur_user.phone = phone_number
    cur_user.save()

    app_logger.info(f"Пользователь {cur_user.full_name} отправил номер телефона: {phone_number}")
    bot.reply_to(message, "Ваш номер успешно сохранен.")


@bot.message_handler(commands=["send_birthdate"])
def send_birthdate_handler(message: Message):
    """ Хендлер для отправки даты рождения """
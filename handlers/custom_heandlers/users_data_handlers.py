import datetime

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
    bot.send_message(message.from_user.id, "Какие данные вы хотите добавить?", reply_markup=users_data_markup())
    bot.set_state(message.from_user.id, UsersDataStates.get_data_state)


@bot.callback_query_handler(func=None, state=UsersDataStates.get_data_state)
def get_data_handler(call):
    """ Хендлер для дальнейшего распределения ввода пользовательских данных """
    bot.answer_callback_query(callback_query_id=call.id)
    if call.data == "Contact":
        bot.send_message(call.from_user.id, "Нажмите на кнопку ниже", reply_markup=send_phone_reply())
        bot.set_state(call.from_user.id, None)
    elif call.data == "Birthdate":
        bot.send_message(call.from_user.id, "Пожалуйста, напишите вашу дату рождения в формате День.Месяц.Год (31.01.2000)")
        bot.set_state(call.from_user.id, UsersDataStates.get_birthdate)


@bot.message_handler(state=UsersDataStates.get_birthdate)
def get_birthdate_handler(message: Message):
    """ Хендлер для сохранения даты рождения пользателя """

    user = User.get(User.user_id == message.from_user.id)
    try:
        user_birthday_list = [int(elem) for elem in message.text.split(".")]
        user_birthday = datetime.date(year=user_birthday_list[2], month=user_birthday_list[1],
                                      day=user_birthday_list[0])
    except Exception:
        bot.send_message(message.from_user.id, "Некорректные данные! Попробуйте еще раз!")
        return
    app_logger.info(f"Запрос добавления даты рождения {message.text} от {user.full_name}.")
    user.birthday = user_birthday
    user.save()
    bot.send_message(message.from_user.id, "Дата рождения сохранена. Вы можете записаться на консультацию")

    if (datetime.datetime.now().date() - user_birthday).days <= 7665:
        app_logger.warning(f"Внимание! Пользователь {user.full_name} слишком малой! Ему менее 21 года ({message.text})")
        bot.send_message(message.from_user.id, "ВАЖНО! Чтобы я могла записать вас на консультацию, "
                                          "ваш возраст должен быть не менее 21 года.")
    bot.set_state(message.from_user.id, None)



@bot.message_handler(content_types=["contact"])
def get_phone_handler(message: Message):
    """ Хендлер для получения номера телефона """

    phone_number = message.contact.phone_number
    cur_user = User.get(User.user_id == message.from_user.id)
    cur_user.phone = phone_number
    cur_user.save()

    app_logger.info(f"Пользователь {cur_user.full_name} отправил номер телефона: {phone_number}")
    bot.reply_to(message, "Ваш номер успешно сохранен.")

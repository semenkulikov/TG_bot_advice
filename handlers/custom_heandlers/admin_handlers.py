from telebot.types import Message

from config_data.config import ALLOWED_USERS
from database.models import User
from keyboards.inline.accounts import users_markup
from loader import bot, app_logger
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


@bot.callback_query_handler(func=None, state=AdminPanel.get_users)
def get_user(call):
    if call.data == "Exit":
        bot.answer_callback_query(callback_query_id=call.id)
        bot.send_message(call.message.chat.id, "Вы успешно вышли из админ панели.")
        bot.set_state(call.message.chat.id, None)
    else:
        bot.answer_callback_query(callback_query_id=call.id)
        user_obj: User = User.get_by_id(call.data)
        bot.send_message(call.message.chat.id, f"Имя: {user_obj.full_name}\n"
                                               f"Телеграм: @{user_obj.username}\n")

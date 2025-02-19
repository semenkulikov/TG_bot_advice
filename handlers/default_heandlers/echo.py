from telebot.types import Message
from loader import bot
from handlers.custom_heandlers.reservation_handlers import advice_handler
from handlers.custom_heandlers.user_handlers import my_timetables_handler, faq_handler
from handlers.custom_heandlers.users_data_handlers import get_users_data_handler


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния

@bot.message_handler(state=None)
def bot_echo(message: Message):
    if message.text == "Записаться":
        advice_handler(message)
    elif message.text == "Мои записи":
        my_timetables_handler(message)
    elif message.text == "Частые вопросы":
        faq_handler(message)
    elif message.text == "Отправить данные":
        get_users_data_handler(message)
    else:
        bot.reply_to(message, f"Введите любую команду из меню, чтобы я начал работать\n"
                              f"Либо выберите одну из кнопок, которые я вам прислал")

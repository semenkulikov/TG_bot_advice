from telebot.types import Message
from loader import bot
from handlers.custom_heandlers.reservation_handlers import advice_handler
from handlers.custom_heandlers.user_handlers import my_advices_handler, faq_handler


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния

@bot.message_handler(state=None)
def bot_echo(message: Message):
    if message.text == "Записаться":
        advice_handler(message)
    elif message.text == "Мои записи":
        my_advices_handler(message)
    elif message.text == "Частые вопросы":
        faq_handler(message)
    else:
        bot.reply_to(message, f"Введите любую команду из меню, чтобы я начал работать\n"
                              f"Либо выберите одну из кнопок, которые я вам прислал")

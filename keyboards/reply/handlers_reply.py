from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def handlers_reply() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, False, row_width=2,
                                   input_field_placeholder="Выберите нужную кнопку...")
    keyboard.add(KeyboardButton('Записаться'), KeyboardButton('Мои записи'))
    keyboard.add(KeyboardButton('Частые вопросы'))
    keyboard.add(KeyboardButton("Отправить данные"))
    return keyboard


def send_phone_reply() -> ReplyKeyboardMarkup:
    """ Reply button для отправки своего номера телефона """
    keyboard = ReplyKeyboardMarkup(True, True, row_width=1,
                                   input_field_placeholder="Нажмите на кнопку ниже...")
    keyboard.add(KeyboardButton("Отправить номер телефона", request_contact=True))
    return keyboard

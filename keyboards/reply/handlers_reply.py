from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def handlers_reply() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, False, row_width=2,
                                   input_field_placeholder="Выберите нужную кнопку...")
    keyboard.add(KeyboardButton('Записаться'), KeyboardButton('Мои записи'))
    keyboard.add(KeyboardButton('Частые вопросы'))
    return keyboard

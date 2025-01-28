from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def handlers_reply() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True, row_width=2,
                                   input_field_placeholder="Нажмите на нужную кнопку...")
    keyboard.add(KeyboardButton('Test button'), KeyboardButton('Test button 2'))
    keyboard.add(KeyboardButton('Test 3'))
    keyboard.add(KeyboardButton('Test 4'))
    return keyboard

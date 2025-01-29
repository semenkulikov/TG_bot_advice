from telebot.handler_backends import State, StatesGroup


class AdminPanel(StatesGroup):
    get_users = State()

class ReservationStates(StatesGroup):
    """ Состояния для хендлеров бронирования """
    get_mode = State()
    get_date = State()
    get_time = State()


class UsersDataStates(StatesGroup):
    """ Состояния для пользовательских данных """
    get_data_state = State()
    get_birthdate = State()